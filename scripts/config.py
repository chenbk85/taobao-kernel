# Configs for various python scripts

# The version of the main tarball to use
# This is the version number of Redhat Enterprise Linux as our build's base.
# Our base version can be tripped out from it.
SRCVERSION = "2.6.32-71.7.1.el6"
# Variant of the kernel-source package, it's useless for now.
# This is supposed to be used to different the various kernels for different platforms and
# applications in the future
# [zyh] we should set VARIANT to things like 'datacenter', 'hadoop', 'search', etc in the
# different git branches.
VARIANT = "tbpublic"
BUILD_DIR = "taobao-kernel-build"
# Supported archs, x86_64 only for now.
flavor_archs = ['x86_64']

# macros to be replaced
DISTRO_BUILD = "71.7.1"
BASE_SUBLEVEL = 32

MACROS = {
    # These are relevant to release process, I hard code them here
    # until we set down the process.
        "RELEASED_KERNEL":0,
#          "BUILD": "71.7.1",
#         "SUBLEVEL": 32,
          "RCREV": 0, # 1 if it's a RC
          "GITREV": 0, # These two ones are useless now.
}
# Whether we are under a git repo
import os, subprocess
def whether_using_git():
    using = True
    IGNORE = open("/dev/null", "w")
	ret = 1
    try:
        git = subprocess.Popen(["git", "rev-parse", "HEAD"], stdout = IGNORE, stderr = IGNORE)
        ret = git.wait()
    except:
        using = False
    if ret:
        using = False
    IGNORE.close()
    return using

def get_branch_name():
    scripts_dir = os.getcwd()
    branch_name = ""
    try:
        head_name = os.path.join(scripts_dir,  "..",  ".git", "HEAD")
        sed = subprocess.Popen(["sed", "-ne", "s|^ref: refs/heads/||p", head_name], stdout=subprocess.PIPE).communicate()[0].split("\n")
        branch_name = sed[0]
    except:
        branch_name = "unknown-branch"
    return branch_name
