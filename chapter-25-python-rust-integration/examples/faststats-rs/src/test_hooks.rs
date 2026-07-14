//! Test-only rendezvous. This file is excluded from Cargo packages and release artifacts.

use std::sync::{Condvar, LazyLock, Mutex};
use std::time::Duration;

#[derive(Default)]
struct State {
    waiting: usize,
    generation: usize,
}

static RENDEZVOUS: LazyLock<(Mutex<State>, Condvar)> =
    LazyLock::new(|| (Mutex::new(State::default()), Condvar::new()));

pub fn wait_for_pair() -> Result<(), &'static str> {
    let (lock, ready) = &*RENDEZVOUS;
    let mut state = lock.lock().map_err(|_| "rendezvous mutex was poisoned")?;
    let generation = state.generation;
    state.waiting += 1;
    if state.waiting == 2 {
        state.waiting = 0;
        state.generation += 1;
        ready.notify_all();
        return Ok(());
    }
    let (mut state, timeout) = ready
        .wait_timeout_while(state, Duration::from_secs(1), |current| {
            current.generation == generation
        })
        .map_err(|_| "rendezvous mutex was poisoned")?;
    if timeout.timed_out() && state.generation == generation {
        state.waiting = state.waiting.saturating_sub(1);
        return Err("two detached calls did not enter concurrently");
    }
    Ok(())
}
