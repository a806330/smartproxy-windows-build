import pathlib
import sys

p = pathlib.Path("internal/upstream/proxy.go")
s = p.read_text(encoding="utf-8")

if "LOCAL_LOOPBACK_PATCH" in s:
    print("PATCH_ALREADY_APPLIED")
    sys.exit(0)

needle = (
    "func IsCNNode(p *Proxy, checker ChnRouteChecker) (bool, string) {\n"
    "\tif p == nil {\n"
    "\t\treturn false, \"\"\n"
    "\t}\n"
    "\t// 1. Egress country code is CN"
)

repl = (
    "func IsCNNode(p *Proxy, checker ChnRouteChecker) (bool, string) {\n"
    "\tif p == nil {\n"
    "\t\treturn false, \"\"\n"
    "\t}\n"
    "\t// LOCAL_LOOPBACK_PATCH: a local socks5 port is only a forwarding entry.\n"
    "\t// Cloudflare labels its WARP egress as loc=CN (account attribution, not\n"
    "\t// physical location); filtering a loopback upstream by that label drops\n"
    "\t// otherwise valid nodes. Real traffic is still decided by smart dialing.\n"
    "\tif ip := net.ParseIP(p.Host); ip != nil && ip.IsLoopback() {\n"
    "\t\treturn false, \"\"\n"
    "\t}\n"
    "\t// 1. Egress country code is CN"
)

if needle not in s:
    print("PATCH_TARGET_NOT_FOUND")
    sys.exit(1)

p.write_text(s.replace(needle, repl, 1), encoding="utf-8")
print("PATCH_APPLIED=True")
