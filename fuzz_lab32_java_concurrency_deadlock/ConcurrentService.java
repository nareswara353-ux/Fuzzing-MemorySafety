import java.io.File;
import java.io.FileInputStream;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;

public class ConcurrentService {
    private static final Object lockA = new Object();
    private static final Object lockB = new Object();
    private static final AtomicInteger sharedCounter = new AtomicInteger(0);

    public static void executeConcurrentWork(byte[] data) throws Exception {
        if (data == null || data.length < 8) return;

        ByteBuffer bb = ByteBuffer.wrap(data).order(ByteOrder.LITTLE_ENDIAN);
        int magic = bb.getInt();
        if (magic != 0x54485244) return;

        int mode = bb.getInt();
        CountDownLatch startGate = new CountDownLatch(1);
        CountDownLatch endGate = new CountDownLatch(2);

        if (mode == 0xDEAD) {
            Thread t1 = new Thread(() -> {
                try {
                    startGate.await();
                    synchronized (lockA) {
                        Thread.sleep(10);
                        synchronized (lockB) {
                            sharedCounter.incrementAndGet();
                        }
                    }
                } catch (Exception ignored) {
                } finally {
                    endGate.countDown();
                }
            });

            Thread t2 = new Thread(() -> {
                try {
                    startGate.await();
                    synchronized (lockB) {
                        Thread.sleep(10);
                        synchronized (lockA) {
                            sharedCounter.incrementAndGet();
                        }
                    }
                } catch (Exception ignored) {
                } finally {
                    endGate.countDown();
                }
            });

            t1.start();
            t2.start();
            startGate.countDown();

            boolean finished = endGate.await(150, TimeUnit.MILLISECONDS);
            if (!finished) {
                System.err.println("[!] DEADLOCK HIT: Mutually inverted locks blocked execution!");
                throw new IllegalStateException("CONCURRENCY_DEADLOCK_DETECTED");
            }
        } else {
            sharedCounter.incrementAndGet();
            System.out.println("[*] Safe concurrent operation completed.");
        }
    }

    public static void main(String[] args) {
        if (args.length < 1) return;
        try {
            File f = new File(args[0]);
            if (!f.exists() || f.length() == 0 || f.length() > 4096) return;

            FileInputStream fis = new FileInputStream(f);
            byte[] data = new byte[(int) f.length()];
            fis.read(data);
            fis.close();

            executeConcurrentWork(data);
        } catch (IllegalStateException ise) {
            throw ise;
        } catch (Exception ignored) {
        }
    }
}
