use tokio::runtime::{Builder, Runtime};
use futures::future::join_all;

/// Engine provides a wrapper around a Tokio runtime capable of executing
/// many tasks concurrently.
pub struct Engine {
    runtime: Runtime,
}

impl Engine {
    /// Create a new engine with the given number of worker threads.
    pub fn new(worker_threads: usize) -> Self {
        let runtime = Builder::new_multi_thread()
            .worker_threads(worker_threads)
            .enable_all()
            .build()
            .expect("failed to build runtime");

        Self { runtime }
    }

    /// Create a new engine sized to the available CPU count.
    pub fn new_auto() -> Self {
        let workers = num_cpus::get();
        Self::new(workers)
    }

    /// Run multiple async tasks and collect their results.
    pub fn run_tasks<F, T>(&self, tasks: Vec<F>) -> Vec<T>
    where
        F: std::future::Future<Output = T> + Send + 'static,
        T: Send + 'static,
    {
        self.runtime.block_on(async { join_all(tasks).await })
    }

    /// Spawn a single future onto the engine.
    pub fn spawn<F, T>(&self, future: F) -> tokio::task::JoinHandle<T>
    where
        F: std::future::Future<Output = T> + Send + 'static,
        T: Send + 'static,
    {
        self.runtime.spawn(future)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn runs_many_tasks() {
        let engine = Engine::new(4);
        let tasks = (0..10)
            .map(|i| async move { i + 1 })
            .collect::<Vec<_>>();
        let results = engine.run_tasks(tasks);
        assert_eq!(results, (1..=10).collect::<Vec<_>>());
    }
}
