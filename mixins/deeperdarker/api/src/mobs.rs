//! `register_goals`: upstream's `registerGoals` for each of the port's mobs,
//! replacing the zombie template's own goals.
//!
//! The template a content living type copies brings its class's goals with it
//! (docs/native-mods.md, "Mob goals"), so each kind clears both selectors and
//! adds what upstream's `content/entities/*.java` adds.
use crate::behaviour::{Hearing, WormCycle, SHATTERED_RADIUS};
use horizon_client::mobs::goals::{
    Float, HurtByTarget, LeapAtTarget, LookAtPlayer, MeleeAttack, NearestTarget, RandomLookAround,
    Stroll,
};
use horizon_client::mobs::goals::{self, Goal};
use horizon_client::mobs::Mob;
use horizon_client::mod_api::RegisterGoalsEvent;

struct Builder<'a> {
    mob: &'a mut Mob,
}

impl Builder<'_> {
    fn reset(&mut self) {
        self.mob.ai.goals.clear();
        self.mob.ai.targets.clear();
    }

    fn goal(&mut self, priority: i32, goal: impl Goal + 'static) {
        self.mob.ai.goals.add(priority, goal);
    }

    fn target(&mut self, priority: i32, goal: impl Goal + 'static) {
        self.mob.ai.targets.add(priority, goal);
    }
}

fn player_target(must_see: bool) -> NearestTarget {
    NearestTarget::player(must_see).reach().interval(10)
}

pub fn register_goals(event: &mut RegisterGoalsEvent<'_>) {
    let kind = event.mob.kind.id.clone();
    let mut b = Builder { mob: event.mob };
    match kind.as_str() {
        // SculkCentipede.registerGoals: a 1.3-speed attacker with a slow
        // stroll and a five-block stare. Upstream's neutral anger is not
        // ported; the centipede hunts players like the rest of the deep dark.
        "deeperdarker:sculk_centipede" => {
            b.reset();
            b.goal(0, Float);
            b.goal(1, MeleeAttack::new(1.3, true));
            b.goal(2, Stroll::avoiding_water(0.9));
            b.goal(3, LookAtPlayer::new(5.0));
            b.goal(4, RandomLookAround::default());
            b.target(1, HurtByTarget::new().alert());
            b.target(2, player_target(false));
        }
        // SculkLeech.registerGoals: small, quick, always hungry.
        "deeperdarker:sculk_leech" => {
            b.reset();
            b.goal(0, Float);
            b.goal(1, MeleeAttack::new(1.1, true));
            b.goal(2, Stroll::new(0.5));
            b.target(1, player_target(true));
        }
        // ShriekWorm: no movement and no stroll. The cycle goal owns its
        // phases and bites at its own reach.
        "deeperdarker:shriek_worm" => {
            b.reset();
            b.goal(0, WormCycle::new());
            b.target(0, player_target(true));
        }
        // Shattered.registerGoals, plus its vibration listening as a target
        // goal: a sound within 16 blocks wakes it.
        "deeperdarker:shattered" => {
            b.reset();
            b.goal(0, Float);
            b.goal(1, MeleeAttack::new(1.4, true));
            b.goal(3, Stroll::avoiding_water(1.0));
            b.goal(4, Stroll::new(0.6));
            b.target(0, Hearing {
                radius: SHATTERED_RADIUS,
            });
            b.target(1, HurtByTarget::new());
        }
        // OvercastPot.registerGoals: leap, then hit.
        "deeperdarker:anger_pot" | "deeperdarker:fear_pot" | "deeperdarker:sorrow_pot" => {
            b.reset();
            b.goal(0, Float);
            b.goal(1, LeapAtTarget::new(0.3));
            b.goal(2, MeleeAttack::new(1.1, true));
            b.goal(3, Stroll::avoiding_water(0.9));
            b.goal(5, RandomLookAround::default());
            b.target(1, HurtByTarget::new());
            b.target(2, player_target(true));
        }
        _ => {}
    }
    let _ = goals::LOOK;
}
