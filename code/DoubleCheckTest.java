// Just compile an run it.
// If you see any 'xxx not initialized' output, then 
// we have verified that the double-check pattern is broken

public class DoubleCheckTest
{


    // static data to aid in creating N singletons
    static final Object dummyObject = new Object(); // for reference init
    static final int A_VALUE = 256; // value to initialize 'a' to
    static final int B_VALUE = 512; // value to initialize 'b' to
    static final int C_VALUE = 1024;
    static ObjectHolder[] singletons;  // array of static references
    static Thread[] threads; // array of racing threads
    static int threadCount; // number of threads to create
    static int singletonCount; // number of singletons to create


    static volatile int recentSingleton;


    // I am going to set a couple of threads racing,
    // trying to create N singletons. Basically the
    // race is to initialize a single array of 
    // singleton references. The threads will use
    // double checked locking to control who 
    // initializes what. Any thread that does not
    // initialize a particular singleton will check 
    // to see if it sees a partially initialized view.
    // To keep from getting accidental synchronization,
    // each singleton is stored in an ObjectHolder 
    // and the ObjectHolder is used for 
    // synchronization. In the end the structure
    // is not exactly a singleton, but should be a
    // close enough approximation.
    // 


    // This class contains data and simulates a 
    // singleton. The static reference is stored in
    // a static array in DoubleCheckFail.
    static class Singleton
    {
        public int a;
        public int b;
        public int c;
        public Object dummy;

        public Singleton()
        {
            a = A_VALUE;
            b = B_VALUE;
            c = C_VALUE;
            dummy = dummyObject;
        }
    }

    static void checkSingleton(Singleton s, int index)
    {
        int s_a = s.a;
        int s_b = s.b;
        int s_c = s.c;
        Object s_d = s.dummy;
        if(s_a != A_VALUE)
            System.out.println("[" + index + "] Singleton.a not initialized " +
                    s_a);
        if(s_b != B_VALUE)
            System.out.println("[" + index 
                    + "] Singleton.b not intialized " + s_b);

        if(s_c != C_VALUE)
            System.out.println("[" + index 
                    + "] Singleton.c not intialized " + s_c);

        if(s_d != dummyObject)
            if(s_d == null)
                System.out.println("[" + index 
                        + "] Singleton.dummy not initialized," 
                        + " value is null");
            else
                System.out.println("[" + index 
                        + "] Singleton.dummy not initialized," 
                        + " value is garbage");
    }

    // Holder used for synchronization of 
    // singleton initialization. 
    static class ObjectHolder
    {
        public Singleton reference;
    }

    static class TestThread implements Runnable
    {
        public void run()
        {
            for(int i = 0; i < singletonCount; ++i)
            {
                ObjectHolder o = singletons[i];
                if(o.reference == null)
                {
                    synchronized(o)
                    {
                        if (o.reference == null) {
                            o.reference = new Singleton();
                            recentSingleton = i;
                        }
                        // shouldn't have to check singelton here
                        // mutex should provide consistent view
                    }
                }
                else {
                    checkSingleton(o.reference, i);
                    int j = recentSingleton-1;
                    if (j > i) i = j;
                }
            } 
        }
    }

    public static void main(String[] args)
    {
        if( args.length != 2 )
        {
            System.err.println("usage: java DoubleCheckFail" +
                    " <numThreads> <numSingletons>");
        }
        // read values from args
        threadCount = Integer.parseInt(args[0]);
        singletonCount = Integer.parseInt(args[1]);

        // create arrays
        threads = new Thread[threadCount];
        singletons = new ObjectHolder[singletonCount];

        // fill singleton array
        for(int i = 0; i < singletonCount; ++i)
            singletons[i] = new ObjectHolder();

        // fill thread array
        for(int i = 0; i < threadCount; ++i)
            threads[i] = new Thread( new TestThread() );

        // start threads
        for(int i = 0; i < threadCount; ++i)
            threads[i].start();

        // wait for threads to finish
        for(int i = 0; i < threadCount; ++i)
        {
            try
            {
                System.out.println("waiting to join " + i);
                threads[i].join();
            }
            catch(InterruptedException ex)
            {
                System.out.println("interrupted");
            }
        }
        System.out.println("done");
    }
}
