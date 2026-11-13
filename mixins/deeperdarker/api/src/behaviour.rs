//! The behaviour the zombie template does not have: the shriek worm's
//! emerge/idle/dig cycle, the shattered's ear for vibrations, and the two
//! sides' shared knowledge of which kinds are this mod's.
//!
//! Upstream's Java mobs (`content/entities/*.java` in the 26.1 branch, GPL-3.0)
//! are the reference; the code here is Horizon's own, written against the
//! vanilla behaviours those classes build on.
use horizon_client::mobs::ai::do_hurt_target;
use horizon_client::mobs::goals::{self, Cx, Goal};
use horizon_client::mobs::{Mob, Who};
use horizon_client::mod_api::{EntityTickPostEvent, Host};
use std::sync::Mutex;
use std::time::{Duration, Instant};

/// The mobs this mod declares, as `data/deeperdarker/horizon/entity_type/`.
pub const KINDS: [&str; 7] = [
    "deeperdarker:sculk_centipede",
    "deeperdarker:sculk_leech",
    "deeperdarker:shriek_worm",
    "deeperdarker:shattered",
    "deeperdarker:anger_pot",
    "deeperdarker:fear_pot",
    "deeperdarker:sorrow_pot",
];

/// Upstream's `ShriekWorm`: 80 ticks to climb out, 1200 standing, 83 to dig
/// back in (`EmergeTime`, `IdleTime`, `DescentTime`).
pub const EMERGE_TICKS: i32 = 80;
pub const IDLE_TICKS: i32 = 1200;
pub const DIG_TICKS: i32 = 83;
/// Upstream's `MeleeAttackGoal` tick interval after a shriek worm's bite
/// (`attackCooldown = 21`).
pub const BITE_COOLDOWN: i32 = 21;
/// Upstream's `getAttackBoundingBox(3)` from the worm's 0.5-wide box: about
/// 3.5 blocks from its centre.
pub const WORM_REACH_SQR: f64 = 3.5 * 3.5;
/// Upstream's shattered listens over 16 blocks (`VibrationUser`).
pub const SHATTERED_RADIUS: f64 = 16.0;
/// A rumour of a vibration lasts about a second and a half.
pub const RUMOUR_AGE: Duration = Duration::from_millis(1500);

pub fn is_our_mob(kind: &str) -> bool {
    KINDS.contains(&kind)
}

/// A sound the shattered may have heard, and when it was made.
struct Rumour {
    at: Instant,
    pos: [f64; 3],
}

static RUMOURS: Mutex<Vec<Rumour>> = Mutex::new(Vec::new());

/// Forgets every rumour; a world opening or closing starts clean.
pub fn reset() {
    if let Ok(mut rumours) = RUMOURS.lock() {
        rumours.clear();
    }
}

/// `native_game_event`: the game events of the level, as the shattered hears
/// them (`GameEventTags.WARDEN_CAN_LISTEN` is every event sculk listens to).
pub fn record_event(_event: &str, pos: [f64; 3]) {
    let Ok(mut rumours) = RUMOURS.lock() else {
        return;
    };
    if rumours.len() >= 64 {
        rumours.remove(0);
    }
    rumours.push(Rumour {
        at: Instant::now(),
        pos,
    });
}

/// Whether a sound near `pos` was made within `age`.
pub fn heard(pos: [f64; 3], radius: f64, now: Instant, age: Duration) -> bool {
    let Ok(rumours) = RUMOURS.lock() else {
        return false;
    };
    let r2 = radius * radius;
    rumours.iter().any(|rumour| {
        now.duration_since(rumour.at) <= age && distance_sqr(pos, rumour.pos) <= r2
    })
}

fn distance_sqr(a: [f64; 3], b: [f64; 3]) -> f64 {
    let (dx, dy, dz) = (a[0] - b[0], a[1] - b[1], a[2] - b[2]);
    dx * dx + dy * dy + dz * dz
}

// ---------------------------------------------------------------------------
// Shriek worm
// ---------------------------------------------------------------------------

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum WormPhase {
    /// Climbing out of the ground: invulnerable, no target.
    Emerging,
    /// Out of the ground, biting what it can reach.
    Idle,
    /// Digging back in: no target, then infested sculk and gone.
    Digging,
}

/// One finished dig, for `native_entity_tick_post` to turn into a block.
struct Dig {
    id: u32,
    pos: [i32; 3],
}

static DIGS: Mutex<Vec<Dig>> = Mutex::new(Vec::new());

fn queue_dig(id: u32, pos: [i32; 3]) {
    let Ok(mut digs) = DIGS.lock() else {
        return;
    };
    if !digs.iter().any(|dig| dig.id == id) {
        digs.push(Dig { id, pos });
    }
}

/// The shriek worm is a stationary trap: it climbs out where it was buried,
/// bites whatever stands within its reach, and after a minute of watching
/// digs back in, leaving infested sculk behind.
#[derive(Clone, Debug)]
pub struct WormCycle {
    phase: WormPhase,
    ticks: i32,
    bite: i32,
}

impl WormCycle {
    pub fn new() -> Self {
        Self {
            phase: WormPhase::Emerging,
            ticks: 0,
            bite: 0,
        }
    }

    fn tick_bite(&mut self, m: &mut Mob, cx: &mut Cx) {
        if self.bite > 0 {
            self.bite -= 1;
            return;
        }
        let Some(who) = m.ai.target else {
            return;
        };
        let Some(info) = m.target_info(cx.w) else {
            return;
        };
        let pos = [m.position.x, m.position.y, m.position.z];
        let target = [info.position.x, info.position.y, info.position.z];
        if distance_sqr(pos, target) > WORM_REACH_SQR {
            return;
        }
        do_hurt_target(m, who, cx);
        self.bite = BITE_COOLDOWN;
    }
}

impl Goal for WormCycle {
    fn flags(&self) -> u8 {
        goals::MOVE | goals::LOOK
    }

    fn can_use(&mut self, _m: &mut Mob, _cx: &mut Cx) -> bool {
        true
    }

    fn can_continue(&mut self, _m: &mut Mob, _cx: &mut Cx) -> bool {
        true
    }

    fn every_tick(&self) -> bool {
        true
    }

    fn tick(&mut self, m: &mut Mob, cx: &mut Cx) {
        self.ticks += 1;
        match self.phase {
            WormPhase::Emerging => {
                m.invulnerable_flag = true;
                m.ai.target = None;
                if emerge_done(self.ticks) {
                    self.phase = WormPhase::Idle;
                    self.ticks = 0;
                    m.invulnerable_flag = false;
                }
            }
            WormPhase::Idle => {
                m.invulnerable_flag = false;
                if self.ticks >= IDLE_TICKS {
                    self.phase = WormPhase::Digging;
                    self.ticks = 0;
                    m.ai.target = None;
                    m.ai.nav.stop();
                    return;
                }
                self.tick_bite(m, cx);
            }
            WormPhase::Digging => {
                m.ai.target = None;
                m.invulnerable_flag = true;
                if dig_done(self.ticks) {
                    let pos = [
                        m.position.x.floor() as i32,
                        m.position.y.floor() as i32,
                        m.position.z.floor() as i32,
                    ];
                    queue_dig(m.id, pos);
                }
            }
        }
    }

    fn box_clone(&self) -> Box<dyn Goal> {
        Box::new(self.clone())
    }

    fn name(&self) -> &'static str {
        "DeeperDarkerShriekWormCycle"
    }
}

pub fn emerge_done(ticks: i32) -> bool {
    ticks > EMERGE_TICKS
}

pub fn dig_done(ticks: i32) -> bool {
    ticks >= DIG_TICKS
}

/// `entity_tick_post`: a worm that finished digging leaves infested sculk and
/// goes away, as upstream's `ShriekWorm.tick` does.
pub fn tick_post(host: &mut dyn Host, event: &EntityTickPostEvent<'_>) {
    let Ok(mut digs) = DIGS.lock() else {
        return;
    };
    let Some(index) = digs.iter().position(|dig| dig.id == event.entity) else {
        return;
    };
    let dig = digs.remove(index);
    drop(digs);
    if let Some(state) = host.default_state("deeperdarker:infested_sculk") {
        host.set_block(event.dimension, dig.pos, state, 3);
    }
    host.remove_mob(event.dimension, dig.id);
}

// ---------------------------------------------------------------------------
// Shattered
// ---------------------------------------------------------------------------

/// The shattered has no eyes: a sound near it is a target, as upstream's
/// `VibrationSystem` `VibrationUser.onReceiveVibration` sets one.
#[derive(Clone, Debug)]
pub struct Hearing {
    pub radius: f64,
}

impl Goal for Hearing {
    fn flags(&self) -> u8 {
        goals::TARGET
    }

    fn can_use(&mut self, m: &mut Mob, cx: &mut Cx) -> bool {
        m.ai.target.is_none()
            && cx.w.player.is_some()
            && heard(
                [m.position.x, m.position.y, m.position.z],
                self.radius,
                Instant::now(),
                RUMOUR_AGE,
            )
    }

    fn can_continue(&mut self, _m: &mut Mob, _cx: &mut Cx) -> bool {
        false
    }

    fn start(&mut self, m: &mut Mob, _cx: &mut Cx) {
        m.ai.target = Some(Who::Player);
    }

    fn box_clone(&self) -> Box<dyn Goal> {
        Box::new(self.clone())
    }

    fn name(&self) -> &'static str {
        "DeeperDarkerShatteredHearing"
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn our_kinds_are_the_declared_ones() {
        assert!(is_our_mob("deeperdarker:sculk_leech"));
        assert!(!is_our_mob("minecraft:zombie"));
        assert!(!is_our_mob("deeperdarker:stalker"));
    }

    #[test]
    fn worm_phase_timings_match_upstream() {
        assert!(!emerge_done(EMERGE_TICKS));
        assert!(emerge_done(EMERGE_TICKS + 1));
        assert!(!dig_done(DIG_TICKS - 1));
        assert!(dig_done(DIG_TICKS));
        assert!(IDLE_TICKS > EMERGE_TICKS);
    }

    #[test]
    fn a_rumour_is_heard_within_its_radius_and_age() {
        reset();
        let now = Instant::now();
        record_event("minecraft:step", [0.0, 0.0, 0.0]);
        assert!(heard([10.0, 0.0, 0.0], 16.0, now, RUMOUR_AGE));
        assert!(!heard([20.0, 0.0, 0.0], 16.0, now, RUMOUR_AGE));
        assert!(!heard([0.0, 0.0, 0.0], 16.0, now + RUMOUR_AGE * 2, RUMOUR_AGE));
        reset();
        assert!(!heard([0.0, 0.0, 0.0], 16.0, now, RUMOUR_AGE));
    }

    #[test]
    fn reach_is_the_worms_attack_box() {
        assert!(WORM_REACH_SQR > 9.0);
        assert!(distance_sqr([0.0; 3], [3.0, 0.0, 0.0]) <= WORM_REACH_SQR);
        assert!(distance_sqr([0.0; 3], [4.0, 0.0, 0.0]) > WORM_REACH_SQR);
    }
}
