import frida
import time

PROCESS = "COSMOTE Connect 3G.exe"

script_code = r"""
var modules = Process.enumerateModulesSync();
var base = null;

for (var i = 0; i < modules.length; i++) {
    if (modules[i].name.toLowerCase() == "atcomm.dll") {
        base = modules[i].base;
        send("FOUND atcomm.dll");
        send("BASE = " + base);
        send("SIZE = " + modules[i].size);
        break;
    }
}

if (base === null) {
    send("ERROR: atcomm.dll was not found");
} else {

    var targets = [
        ["SRVGetSysInfo",       0x4300],
        ["SRVGetSrvStatus",     0x3E70],
        ["SRVGetSignalQuality", 0x3F60],
        ["SRVGetSimStatus",     0x40D0],
        ["SRVGetSystemMode",    0x3EC0],
        ["SRVGetPSState",       0x50A0]
    ];

    for (var i = 0; i < targets.length; i++) {

        var name = targets[i][0];
        var rva = targets[i][1];
        var address = base.add(rva);

        send(
            "TARGET " + name +
            " RVA=0x" + rva.toString(16) +
            " ADDRESS=" + address
        );

        try {

            (function(funcName, funcAddress) {

                Interceptor.attach(funcAddress, {

                    onEnter: function(args) {
                        this.funcName = funcName;

                        send(
                            "CALL " + funcName +
                            " this=" + args[0]
                        );
                    },

                    onLeave: function(retval) {
                        send(
                            "RETURN " + this.funcName +
                            " = " + retval
                        );
                    }

                });

            })(name, address);

        } catch (e) {

            send(
                "HOOK ERROR " + name +
                " : " + e
            );
        }
    }
}
"""

def on_message(message, data):
    if message["type"] == "send":
        print(message["payload"])
    else:
        print(message)

print("Attaching...")

session = frida.attach(PROCESS)

script = session.create_script(script_code)
script.on("message", on_message)
script.load()

print()
print("Tracing active.")
print("Use COSMOTE Connect until it shows Limited service.")
print("Press Ctrl+C to stop.")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    session.detach()