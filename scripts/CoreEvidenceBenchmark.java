// SPDX-License-Identifier: MIT
// V2: exact-release TSC microbenchmark. NEVER a Minecraft/Fabric MSPT measurement.
// Uses the released Simulator's *private* tick(long) as a deterministic bytecode oracle.
// Unlike public tick(), that internal method does not consult wall clock for catch-up.
import java.lang.management.BufferPoolMXBean;
import java.lang.management.GarbageCollectorMXBean;
import java.lang.management.ManagementFactory;
import java.lang.management.MemoryMXBean;
import java.lang.reflect.Method;
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

public final class CoreEvidenceBenchmark {
    private static final String DIMENSION = "goldrail-evidence-synthetic";
    private static final long INITIAL_VIRTUAL_MILLIS = 1720000000000L;
    private static final long VIRTUAL_STEP_MILLIS = 1000L;

    private static final class FixtureSimulator extends Simulator {
        FixtureSimulator(Path root) {
            super(DIMENSION, new String[]{DIMENSION}, root, false);
        }
        void initializeClock() { setCurrentMillis(INITIAL_VIRTUAL_MILLIS); }
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

    private static void phase(String name) {
        System.out.println("PHASE|" + name + "|" + System.nanoTime());
        System.out.flush();
    }

    private static long gcValue(boolean time) {
        long total = 0;
        for (GarbageCollectorMXBean bean : ManagementFactory.getGarbageCollectorMXBeans()) {
            long amount = time ? bean.getCollectionTime() : bean.getCollectionCount();
            if (amount > 0) total += amount;
        }
        return total;
    }

    private static void step(Method internalTick, FixtureSimulator simulator) throws Exception {
        long before = simulator.getCurrentMillis();
        internalTick.invoke(simulator, VIRTUAL_STEP_MILLIS);
        long after = simulator.getCurrentMillis();
        if (after - before != VIRTUAL_STEP_MILLIS)
            throw new IllegalStateException("Released private tick did not advance exactly 1000ms");
    }

    private static void pace(long targetNanos) throws InterruptedException {
        long remaining = targetNanos - System.nanoTime();
        if (remaining > 0) {
            Thread.sleep(remaining / 1000000L, (int)(remaining % 1000000L));
        }
    }

    public static void main(String[] args) throws Exception {
        if (args.length != 5) throw new IllegalArgumentException(
            "scratch-root rails warmup-seconds measured-calls pacing-ms required"
        );
        Path root = Path.of(args[0]).toAbsolutePath().normalize();
        if (Files.exists(root)) throw new IllegalArgumentException("Scratch root already exists");
        int rails = Integer.parseInt(args[1]);
        int warmupSeconds = Integer.parseInt(args[2]);
        int samples = Integer.parseInt(args[3]);
        int pacingMs = Integer.parseInt(args[4]);
        if (rails < 0 || rails > 1024 || warmupSeconds < 1 || warmupSeconds > 90 ||
            samples < 20 || samples > 1000 || pacingMs < 20 || pacingMs > 250)
            throw new IllegalArgumentException("Unsafe or invalid fixture parameters");
        phase("startup");
        FixtureSimulator simulator = new FixtureSimulator(root);
        for (int i = 0; i < rails; i++) {
            Rail item = rail(i);
            if (!item.isValid()) throw new IllegalStateException("Invalid synthetic rail");
            simulator.rails.add(item);
        }
        simulator.sync();
        if (simulator.rails.size() != rails) throw new IllegalStateException("Rail count differs");
        simulator.initializeClock();
        // Reflective access is intentionally limited to the exact published Java bytecode.
        Method internalTick = Simulator.class.getDeclaredMethod("tick", long.class);
        internalTick.setAccessible(true);
        phase("warmup");
        long warmupStart = System.nanoTime();
        long deadline = warmupStart + warmupSeconds * 1000000000L;
        long next = warmupStart;
        int warmedCalls = 0;
        while (System.nanoTime() < deadline) {
            step(internalTick, simulator);
            warmedCalls++;
            next += pacingMs * 1000000L;
            pace(next);
        }
        long warmupActualNs = System.nanoTime() - warmupStart;
        long virtualBefore = simulator.getCurrentMillis();
        phase("ticks");
        long gcCountBefore = gcValue(false), gcTimeBefore = gcValue(true);
        com.sun.management.ThreadMXBean threads =
            (com.sun.management.ThreadMXBean) ManagementFactory.getThreadMXBean();
        long threadId = Thread.currentThread().threadId();
        boolean allocationSupported = threads.isThreadAllocatedMemorySupported();
        if (allocationSupported) threads.setThreadAllocatedMemoryEnabled(true);
        long allocationBefore = allocationSupported ? threads.getThreadAllocatedBytes(threadId) : -1;
        StringJoiner sampleTimes = new StringJoiner(",");
        long measuredStart = System.nanoTime();
        long nextMeasured = measuredStart;
        for (int i = 0; i < samples; i++) {
            long start = System.nanoTime();
            step(internalTick, simulator);
            sampleTimes.add(String.format(Locale.ROOT, "%.6f", (System.nanoTime() - start) / 1e6));
            nextMeasured += pacingMs * 1000000L;
            pace(nextMeasured);
        }
        long measuredWallNs = System.nanoTime() - measuredStart;
        long virtualAfter = simulator.getCurrentMillis();
        if (virtualAfter - virtualBefore != samples * VIRTUAL_STEP_MILLIS)
            throw new IllegalStateException("Virtual clock drift");
        long allocated = allocationSupported
            ? threads.getThreadAllocatedBytes(threadId) - allocationBefore : -1;
        long gcCollections = gcValue(false) - gcCountBefore;
        long gcMillis = gcValue(true) - gcTimeBefore;
        MemoryMXBean memory = ManagementFactory.getMemoryMXBean();
        long heapUsed = memory.getHeapMemoryUsage().getUsed();
        long heapCommitted = memory.getHeapMemoryUsage().getCommitted();
        long directBytes = 0;
        for (BufferPoolMXBean pool : ManagementFactory.getPlatformMXBeans(BufferPoolMXBean.class)) {
            if ("direct".equals(pool.getName())) directBytes += pool.getMemoryUsed();
        }

        phase("save");
        simulator.stop();
        phase("reload");
        FixtureSimulator reload = new FixtureSimulator(root);
        int loaded = reload.rails.size();
        if (loaded != rails) throw new IllegalStateException("Count-only save/reload failed");
        reload.stop();
        phase("idle");
        Thread.sleep(700);
        phase("done");
        System.out.println("RESULT|" + rails + "|" + samples + "|" + sampleTimes + "|" +
            heapUsed + "|" + heapCommitted + "|" + directBytes + "|" +
            gcCollections + "|" + gcMillis + "|" + allocated + "|" + loaded + "|" +
            warmedCalls + "|" + warmupActualNs + "|" + measuredWallNs + "|" +
            virtualBefore + "|" + virtualAfter);
        System.out.flush();
    }
}
