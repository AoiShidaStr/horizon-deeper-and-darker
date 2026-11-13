//! Deeper and Darker for Horizon: the native (trait mod) half.
//!
//! A Horizon port of Deeper and Darker by Kyanite Mods (GPL-3.0; see LICENSE
//! and NOTICE.md in the mod folder). This crate gives the content half's
//! living types their goals and the behaviour the zombie template does not
//! have: the sculk centipede and leech hunt, the shriek worm waits in the
//! ground and buries itself again, the shattered hears vibrations, the
//! overcast pots leap at players.
//!
//! The launcher links this crate into the game and calls `hooks()`
//! (docs/native-mods.md, "Trait mods"). A dedicated server only fires the
//! server hooks; nothing here draws.
pub mod behaviour;
mod mobs;

use horizon_client::mod_api::{
    EntityTickPostEvent, Flow, GameEventEvent, Host, Hooks, LivingConversionPreEvent,
    RegisterGoalsEvent, WorldLifecycleEvent, WorldPhase,
};

pub fn hooks() -> Box<dyn Hooks> {
    Box::new(Mod)
}

struct Mod;

impl Hooks for Mod {
    fn register_goals(&self, event: &mut RegisterGoalsEvent<'_>) {
        mobs::register_goals(event);
    }

    fn world_lifecycle(&self, _host: &mut dyn Host, event: &mut WorldLifecycleEvent<'_>) {
        if matches!(
            event.phase,
            WorldPhase::WorldOpenReady | WorldPhase::WorldCloseFinal
        ) {
            behaviour::reset();
        }
    }

    /// A game event is the sculk world's sound: the shattered hears it.
    fn game_event(&self, _host: &mut dyn Host, event: &mut GameEventEvent<'_>) {
        behaviour::record_event(event.event, event.pos);
    }

    /// The shriek worm that finished digging places infested sculk where it
    /// stood and goes away, as upstream's `ShriekWorm.tick` does.
    fn entity_tick_post(&self, host: &mut dyn Host, event: &mut EntityTickPostEvent<'_>) {
        behaviour::tick_post(host, event);
    }

    /// Upstream's mobs never turn into drowned (only the zombie template's
    /// class does).
    fn living_conversion_pre(
        &self,
        _host: &mut dyn Host,
        event: &mut LivingConversionPreEvent<'_>,
    ) -> Flow {
        if behaviour::is_our_mob(event.kind) {
            Flow::Cancel
        } else {
            Flow::Continue
        }
    }
}
