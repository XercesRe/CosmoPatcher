import frida
import time

PROCESS = "COSMOTE Connect 3G.exe"

session = frida.attach(PROCESS)

js = r'''
"use strict";

console.log("[+] COSMOTE NETCONNECT LIVE BRIDGE");
console.log("[+] Target: NetConnectPlugin.dll");


function findModule(name) {

    var mods = Process.enumerateModules();

    for (var i = 0; i < mods.length; i++) {

        if (
            mods[i].name.toLowerCase() ==
            name.toLowerCase()
        ) {
            return mods[i];
        }
    }

    return null;
}


var net =
    findModule("NetConnectPlugin.dll");

if (net === null) {
    throw new Error(
        "NetConnectPlugin.dll not loaded"
    );
}


var base = net.base;
var size = net.size;

console.log(
    "[+] NetConnectPlugin base = " +
    base
);

console.log(
    "[+] NetConnectPlugin size = 0x" +
    size.toString(16)
);


/*
 * =====================================================
 * IMPORTANT STATIC ADDRESSES WE ALREADY FOUND
 * =====================================================
 */

var wifiMeta =
    base.add(0x3f56c);

var dialMeta =
    base.add(0x3f530);

var ndisMeta =
    base.add(0x3f550);

var netMeta =
    base.add(0x3f704);


console.log(
    "[+] IWiFiManService metadata = " +
    wifiMeta
);

console.log(
    "[+] IDialUpService metadata = " +
    dialMeta
);

console.log(
    "[+] INDISService metadata = " +
    ndisMeta
);

console.log(
    "[+] INetConnectService metadata = " +
    netMeta
);


/*
 * =====================================================
 * SHOW THE DATA AROUND THE SERVICE METADATA
 * =====================================================
 */

function dumpMeta(name, p) {

    console.log("");
    console.log(
        "========== " +
        name +
        " =========="
    );

    try {

        console.log(
            hexdump(
                p.sub(32),
                {
                    offset: 0,
                    length: 96,
                    header: true,
                    ansi: false
                }
            )
        );

    } catch (e) {

        console.log(
            "[!] dump failed: " +
            e
        );
    }
}


dumpMeta(
    "IWiFiManService",
    wifiMeta
);

dumpMeta(
    "IDialUpService",
    dialMeta
);

dumpMeta(
    "INDISService",
    ndisMeta
);

dumpMeta(
    "INetConnectService",
    netMeta
);


/*
 * =====================================================
 * TRACE CALLS INTO NETCONNECTPLUGIN
 * =====================================================
 *
 * We deliberately don't attach to every byte.
 * Instead we locate executable regions and use a
 * lightweight Stalker trace when the user presses
 * Connect/Redial.
 */


/*
 * Find likely service-related code around the
 * known Wi-Fi strings.
 */

var wifiString =
    Memory.scanSync(
        base,
        size,
        "49 57 69 46 69 4D 61 6E 53 65 72 76 69 63 65"
    );


console.log(
    "[+] IWiFiManService string matches = " +
    wifiString.length
);


for (
    var i = 0;
    i < wifiString.length;
    i++
) {

    console.log(
        "[WIFI STRING] " +
        wifiString[i].address
    );
}


/*
 * Search for WLANScan.
 */

var scanString =
    Memory.scanSync(
        base,
        size,
        "57 4C 41 4E 53 63 61 6E"
    );


console.log(
    "[+] WLANScan string matches = " +
    scanString.length
);


for (
    var i = 0;
    i < scanString.length;
    i++
) {

    console.log(
        "[WLANScan] " +
        scanString[i].address
    );
}


/*
 * =====================================================
 * LIVE CALL TRACE
 * =====================================================
 */

var interesting = {};


function record(addr) {

    var key =
        addr.toString();

    if (!interesting[key]) {

        interesting[key] = {
            count: 0,
            first: Date.now()
        };
    }

    interesting[key].count++;

    return interesting[key].count;
}


/*
 * Use Stalker on the main thread only when requested.
 */

var tracing = false;
var traceThread = null;


/*
 * Find the UI thread by observing calls into the
 * plugin.
 */

function startTrace(threadId) {

    if (tracing)
        return;

    tracing = true;
    traceThread = threadId;

    console.log("");
    console.log(
        "=========================================="
    );

    console.log(
        "[+] STARTING NETCONNECT TRACE"
    );

    console.log(
        "[+] Thread ID = " +
        threadId
    );

    console.log(
        "=========================================="
    );


    Stalker.follow(
        threadId,
        {

            events: {
                call: true
            },

            onCallSummary: function(summary) {

                var printed = 0;

                for (
                    var target in summary
                ) {

                    var p =
                        ptr(target);

                    /*
                     * Only report calls into
                     * NetConnectPlugin.dll.
                     */

                    if (
                        p.compare(base) >= 0 &&
                        p.compare(
                            base.add(size)
                        ) < 0
                    ) {

                        var c =
                            summary[target];

                        console.log(
                            "[NETCALL] " +
                            p +
                            " count=" +
                            c
                        );

                        printed++;

                        if (printed >= 80)
                            break;
                    }
                }
            }
        }
    );
}


/*
 * Stop trace after a reasonable period.
 */

function stopTrace() {

    if (!tracing)
        return;

    try {
        Stalker.unfollow(traceThread);
        Stalker.garbageCollect();
    } catch (_) {}

    tracing = false;

    console.log("");
    console.log(
        "[+] NETCONNECT TRACE STOPPED"
    );
}


/*
 * =====================================================
 * HOOK ENTRY POINTS AROUND THE PLUGIN'S MAIN CODE
 * =====================================================
 *
 * We don't patch them yet.
 * We use them to automatically detect the thread
 * COSMOTE uses for Connect/Redial.
 */

var candidates = [
    0x33c45,
    0x33ff5,
    0x3f8f5,
    0x3f92d
];


for (
    var i = 0;
    i < candidates.length;
    i++
) {

    var p =
        base.add(
            candidates[i]
        );

    /*
     * These offsets point at string data, not
     * executable functions. We intentionally do
     * NOT Interceptor.attach() to them.
     */

    console.log(
        "[+] Wi-Fi data location: " +
        p
    );
}


/*
 * =====================================================
 * WATCH ALL THREADS
 * =====================================================
 */

var seenThreads = {};


setInterval(function() {

    var threads =
        Process.enumerateThreads();

    for (
        var i = 0;
        i < threads.length;
        i++
    ) {

        var id =
            threads[i].id;

        if (!seenThreads[id]) {

            seenThreads[id] = true;

            console.log(
                "[THREAD] " +
                id +
                " detected"
            );
        }
    }

}, 1000);


/*
 * =====================================================
 * CONNECTION BUTTON DETECTOR
 * =====================================================
 *
 * Every second we report currently running threads.
 * The actual useful event is the thread whose call
 * stack enters NetConnectPlugin during Connect/Redial.
 */

setInterval(function() {

    var threads =
        Process.enumerateThreads();

    for (
        var i = 0;
        i < threads.length;
        i++
    ) {

        var t =
            threads[i];

        /*
         * Keep this lightweight.
         */

        try {

            var bt =
                Thread.backtrace(
                    t.context,
                    Backtracer.ACCURATE
                );

            for (
                var j = 0;
                j < bt.length;
                j++
            ) {

                var p =
                    bt[j];

                if (
                    p.compare(base) >= 0 &&
                    p.compare(
                        base.add(size)
                    ) < 0
                ) {

                    /*
                     * We found a thread currently
                     * executing NetConnectPlugin.
                     */

                    if (!tracing) {

                        console.log(
                            "[+] NetConnectPlugin activity detected"
                        );

                        console.log(
                            "[+] Thread = " +
                            t.id
                        );

                        startTrace(t.id);
                    }

                    break;
                }
            }

        } catch (_) {}
    }

}, 500);


/*
 * =====================================================
 * PERSISTENT CONNECTION MONITOR
 * =====================================================
 */

setInterval(function() {

    console.log(
        "[MONITOR] COSMOTE NetConnect bridge alive"
    );

}, 5000);


console.log("");
console.log(
    "=========================================="
);

console.log(
    "[+] READY"
);

console.log(
    "[+] Press CONNECT or REDIAL now"
);

console.log(
    "[+] NetConnectPlugin activity will be traced"
);

console.log(
    "[+] No modem state is modified"
);

console.log(
    "=========================================="
);
'''

script = session.create_script(js)


def on_message(message, data):
    if message["type"] == "send":
        print(message["payload"])
    else:
        print(message)


script.on("message", on_message)
script.load()

print("[+] Injected.")
print("[+] Press CONNECT / REDIAL in COSMOTE Connect.")
print("[+] Leave this window running.")

while True:
    time.sleep(1)