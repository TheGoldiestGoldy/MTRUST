// SPDX-License-Identifier: MIT
// Standalone, synthetic-only bench. The production Minecraft server is never contacted.
import java.lang.management.BufferPoolMXBean;
import java.lang.management.GarbageCollectorMXBean;
import java.lang.management.ManagementFactory;
import java.lang.management.MemoryMXBean;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Locale;
import java.util.StringJoiner;
import org.mtr.core.data.Position;
import org.mtr.core.data.Rail;
import org.mtr.core.data.TransportMode;
import org.mtr.core.simulation.Simulator;
import org.mtr.core.tool.Angle;
import org.mtr.libraries.it.unimi.dsi.fastutil.objects.ObjectArrayList;

public final class CoreSyntheticBenchmark {
    private static final String DIMENSION = "goldrail-synthetic";
    private static final class SyntheticSimulator extends Simulator {
        SyntheticSimulator(Path root) {
            super(DIMENSION, new String[] {DIMENSION}, root, false);
        }
        void setSyntheticClock(long timestamp) { setCurrentMillis(timestamp); }
    }

    private static Rail rail(int index) {
        long x = index * 16L;
        return Rail.newRail(
            new Position(x, 64, 0), Angle.E,
            new Position(x + 16, 64, 0), Angle.E,
            Rail.Shape.QUADRATIC, 0.0, 2L,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            new ObjectArrayList<String>(),
            80, 80, false, false, true, false, false, TransportMode.TRAIN
        );
    }

    private static long gcCount() {
        long count = 0;
        for (GarbageCollectorMXBean collector : ManagementFactory.getGarbageCollectorMXBeans()) {
            if (collector.getCollectionCount() > 0) count += collector.getCollectionCount();
        }
        return count;
    }

    private static long gcMillis() {
        long millis = 0;
        for (GarbageCollectorMXBean collector : ManagementFactory.getGarbageCollectorMXBeans()) {
            if (collector.getCollectionTime() > 0) millis += collector.getCollectionTime();
        }
        return millis;
    }

    public static void main(String[] args) throws Exception {
        if (args.length != 4) {
            throw new IllegalArgumentException("Expected scratch-root, rail-count, warmup-ticks, sample-ticks");
        }
        Path root = Path.of(args[0]).toAbsolutePath().normalize();
        if (Files.exists(root)) throw new IllegalArgumentException("Scratch root must not exist");
        int rails = Integer.parseInt(args[1]);
        int warmup = Integer.parseInt(args[2]);
        int samples = Integer.parseInt(args[3]);
        if (rails < 0 || rails > 1024 || warmup < 1 || samples < 5 || samples > 500) {
            throw new IllegalArgumentException("Benchmark limits exceeded");
        }
        SyntheticSimulator simulator = new SyntheticSimulator(root);
        for (int i = 0; i < rails; i++) {
            Rail item = rail(i);
            if (!item.isValid()) throw new IllegalStateException("Generated rail invalid: " + i);
            simulator.rails.add(item);
        }
        simulator.sync();
        if (simulator.rails.size() != rails) throw new IllegalStateException("Topology count mismatch");
        Thread.sleep(100);
        for (int i = 0; i < warmup; i++) {
            simulator.setSyntheticClock(System.currentTimeMillis() - 1000);
            simulator.tick();
        }
        System.out.println("WARMED");
        long gcBefore = gcMillis();
        long gcCountBefore = gcCount();
        com.sun.management.ThreadMXBean threads =
            (com.sun.management.ThreadMXBean) ManagementFactory.getThreadMXBean();
        long threadId = Thread.currentThread().threadId();
        boolean trackAllocations = threads.isThreadAllocatedMemorySupported();
        if (trackAllocations) threads.setThreadAllocatedMemoryEnabled(true);
        long beforeAllocated = trackAllocations ? threads.getThreadAllocatedBytes(threadId) : -1;
        StringJoiner tickSamples = new StringJoiner(",");
        for (int i = 0; i < samples; i++) {
            simulator.setSyntheticClock(System.currentTimeMillis() - 1000);
            long start = System.nanoTime();
            simulator.tick();
            tickSamples.add(String.format(Locale.ROOT, "%.6f", (System.nanoTime() - start) / 1e6));
        }
        long allocated = trackAllocations ? threads.getThreadAllocatedBytes(threadId) - beforeAllocated : -1;
        long gcDelta = gcMillis() - gcBefore;
        long gcCountDelta = gcCount() - gcCountBefore;
        MemoryMXBean memory = ManagementFactory.getMemoryMXBean();
        long heapUsed = memory.getHeapMemoryUsage().getUsed();
        long heapCommitted = memory.getHeapMemoryUsage().getCommitted();
        long directUsed = 0;
        for (BufferPoolMXBean pool : ManagementFactory.getPlatformMXBeans(BufferPoolMXBean.class)) {
            if ("direct".equals(pool.getName())) directUsed += pool.getMemoryUsed();
        }
        simulator.stop(); // synthetic root only; intentional save round-trip
        SyntheticSimulator reload = new SyntheticSimulator(root);
        int loadedRails = reload.rails.size();
        if (loadedRails != rails) throw new IllegalStateException(
            "Synthetic MessagePack save/load mismatch: expected " + rails + " got " + loadedRails
        );
        reload.stop();
        System.out.println("RESULT|" + rails + "|" + samples + "|" + tickSamples + "|" +
            heapUsed + "|" + heapCommitted + "|" + directUsed + "|" + gcCountDelta + "|" +
            gcDelta + "|" + allocated + "|" + loadedRails);
        Thread.sleep(350); // let external /proc sampler observe the process
    }
}
