#!/usr/bin/python

#############################################################################
# Copyright (c) 2010 Taobao.com, Inc.
# All Rights Reserved.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of version 2 of the GNU General Public License as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.   See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, contact Taobao.com, Inc.
#
# To contact Taobao.com about this file by physical or electronic mail,
# you may find current contact information at www.taobao.com
#
#############################################################################

import os, subprocess, sys
import commands, getopt, shutil

import config

patch_start_no = 200
config_start_no = 50

def print_usage ():
    print >>sys.stderr, "Usage: mkspec.py --patches <patches' names, splited with spaces>\n" \
        "--release-string <release string>\n" \
        "--configs <config files' names>\n" \
        "--changelog <Changelog file's name>\n" \
        "[--release <mark for a kernel release>]\n"
    return


def parse_opts ():
    import getopt
    release_string = None
    configs = []
    changelog = None
    released = False
    buildid = ""
    try:
        opts, args = getopt.getopt(sys.argv[1:], "",  \
                                   ["buildid=", "patches=", "release-string=", "configs=", "changelog=", "release", "help"])
        for o, a in opts:
            if o in ("--help"):
                print_usage()
                sys.exit(2)
            if o in ("--patches"):
                patches = a.strip().split(" ")
            if o in ("--buildid"):
                buildid = a.strip()
            if o in ("--release-string"):
                if " " in a.strip():
                    print >>sys.stderr, "--release-string option argument must not contain spaces\n"
                    sys.exit(1)
                release_string = a.strip()
            if o in ("--configs"):
                configs = a.strip().split(" ")
            if o in ("--changelog"):
                changelog = a.strip()
            if o in ("--release"):
                released  = True
    except:
        print_usage()
        sys.exit(2)
    return patches, release_string, configs, changelog, released, buildid

def get_script_loc ():
    path = sys.path[0]
    if os.path.isdir(path):
        return path
    elif os.path.isfile(path):
        return os.path.dirname(path)



if __name__ == "__main__":
    patches, release_string, config_files, changelog, released, buildid = parse_opts()
    script_dir = get_script_loc()
    os.chdir(script_dir)
    os.chdir("..")
    WORKING_DIR = os.getcwd()
    rpm_dir = os.path.join(WORKING_DIR,  "rpm")
    build_dir = os.path.join(WORKING_DIR, config.BUILD_DIR)
    config_dir = os.path.join(WORKING_DIR,  "config")

    spec_temple = "".join(open(os.path.join(rpm_dir,  "kernel.spec.in")).readlines())

    # Generate version number from tags and base kernel version number.
    # tb_base_var is something like 2.6.32
    tb_base_ver = config.SRCVERSION.split("-")[0]
    tb_sublevel = tb_base_ver.split(".")[2]
    if not config.whether_using_git():
        print >>sys.stderr, "I can't proceed without living in a git repo.\n"
        sys.exit(1)
    # tb_tag is something like tb1.1
    tb_tag = commands.getoutput("git tag -l 'tb*'").split("\n")[-1]
    if tb_tag == "" and released:
        print >>sys.stderr, "You want to release a kernel but there is no 'tbx.y' tag.\n"
        sys.exit(1)
    tb_short_commit = commands.getoutput("git log %s --pretty=format:%%h -1" % (tb_tag,))
    tb_long_commit = commands.getoutput("git log %s --pretty=format:%%H -1" % (tb_tag,))

    if released:
        # Update taobao-kernel-history.log
        old_log = os.path.join(rpm_dir, "taobao-kernel-history.log")
        new_log = os.path.join(build_dir, "taobao-kernel-history.log")
        existed = False
        if os.path.exists(old_log):
            shutil.copy(old_log, build_dir)
            logs = open(new_log, "r").readlines()
            for line in logs:
                if tb_tag in line:
                    existed = True
                    break

        if not existed:
            log = open(new_log, "a")
            log.write("%s-%s\tlinux-%s.tar.bz2\t%s\n" % (tb_base_ver, tb_tag, config.SRCVERSION, tb_long_commit))
            log.close()
            shutil.copy(new_log, rpm_dir)
            print >>sys.stdout, "Attention: rpm/taobao-kernel-history.log has been updated with this release.\n" \
                "Please remember to add it when committing.\n"
        config.MACROS["RELEASED_KERNEL"] = 1
    else:
        config.MACROS["RELEASED_KERNEL"] = 0

    if released:
            pkg_release = tb_tag + buildid
    else:
#   comment this out for ABS build.
#            pkg_release = tb_tag + "@git" + tb_short_commit
            pkg_release = tb_tag + buildid + "-" + tb_short_commit

    dynamic_values = {"RPMVERSION" : tb_base_ver,
                      "PKG_RELEASE" : pkg_release,
                      "KVERSION" : config.SRCVERSION,
                      "SUBLEVEL" : tb_sublevel
                      }

    for key in dynamic_values:
        spec_temple = spec_temple.replace("%%" + key + "%%", str(dynamic_values[key]))


    for key in config.MACROS.keys():
        spec_temple = spec_temple.replace("%%" + key + "%%", str(config.MACROS[key]))

    configs = ""
    index = config_start_no
    for cn in config_files:
        configs += "Source%d: %s\n" % (index, cn)
        index +=1
    spec_temple = spec_temple.replace("%%CONFIGS%%", configs)

    text = ""
    applypatch = ""
    index = patch_start_no
    for cn in patches:
        text += "Source%d: %s\n" % (index, cn)
        applypatch +="ApplyPatch %%{SOURCE%d}\n" % (index,)
        index +=1


    spec_temple = spec_temple.replace("%%PATCH_LIST%%", text)
    spec_temple = spec_temple.replace("%%PATCH_APPLICATION%%", applypatch)

    changes = ""
    if changelog:
        changes = commands.getoutput("%s %s" % ( \
            os.path.join(script_dir, "convert_changes_to_rpm_changelog"), \
            changelog))

    spec_temple = spec_temple.replace("%%CHANGELOG%%", changes)

    spec = open(os.path.join(build_dir,  "kernel.spec"), "w")
    spec.write(spec_temple)
    spec.close()
