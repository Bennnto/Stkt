use std::time::Instant;

struct Chunk {
    memory: Vec<u8>,
    capacity: usize,
    offset: usize,
    next: Option<Box<Chunk>>,
}

struct RustArena {
    current: Box<Chunk>,
    default_chunk_size: usize,
}

impl RustArena {
    fn new(chunk_size: usize) -> Self {
        let size = if chunk_size == 0 { 65536 } else { chunk_size };
        let chunk = Box::new(Chunk {
            memory: vec![0u8; size],
            capacity: size,
            offset: 0,
            next: None,
        });
        RustArena {
            current: chunk,
            default_chunk_size: size,
        }
    }

    fn alloc_str(&mut self, s: &str) -> *const u8 {
        let len = s.len() + 1;
        let aligned = (len + 7) & !7;
        if self.current.offset + aligned > self.current.capacity {
            let mut new_cap = self.default_chunk_size;
            if aligned > new_cap {
                new_cap = aligned;
            }
            let old_chunk = std::mem::replace(
                &mut self.current,
                Box::new(Chunk {
                    memory: vec![0u8; new_cap],
                    capacity: new_cap,
                    offset: 0,
                    next: None,
                }),
            );
            self.current.next = Some(old_chunk);
        }
        let ptr = unsafe { self.current.memory.as_ptr().add(self.current.offset) };
        self.current.offset += aligned;
        ptr
    }

    fn reset(&mut self) {
        self.current.offset = 0;
        let mut curr = self.current.next.as_mut();
        while let Some(c) = curr {
            c.offset = 0;
            curr = c.next.as_mut();
        }
    }
}

fn main() {
    println!("=== Rust Memory Arena Benchmark ===");
    println!("Allocating 1,000,000 strings + instant reset...");

    let mut arena = RustArena::new(65536);
    let start = Instant::now();

    for _ in 0..1_000_000 {
        let _ptr = arena.alloc_str("stkt_memory_arena_payload_item");
    }

    let alloc_time = start.elapsed().as_millis();
    println!("Allocation Time (ms):\n{}", alloc_time);

    let reset_start = Instant::now();
    arena.reset();
    let reset_time = reset_start.elapsed().as_millis();
    println!("Reset Time (ms):\n{}", reset_time);

    let total_time = start.elapsed().as_millis();
    println!("Total Time (ms):\n{}", total_time);
}
