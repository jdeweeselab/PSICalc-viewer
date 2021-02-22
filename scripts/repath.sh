#!/bin/bash
# Repathing .dylib's references for packaging within an application
# Author: Roberto Aguilar <roberto.c.aguilar@gmail.com>
#
# With help from Nick Jensen's blog at:
# http://goto11.net/how-to-bundle-a-c-library-with-a-cocoa-application/
#
# All references within the dylib except ones to files in /usr/lib are
# converted over to reference the given root.

# the path that dylibs should use, e.g. @executable_path/../Resources
# the post uses @executable_path/../Resources, but on Mountain Lion without any
# tweaks the files ended up in Resources.
new_root=$1

# path to the dynamic library
dylib=$2

if [ "${new_root}" == "" ] || [ "${dylib}" == "" ]; then
    echo "$(basename $0) <new root> <dylib> # (see comments in source code)" 1>&2;
    exit 1;
fi;

dylib_base=$(basename ${dylib})

otool -L ${dylib} | sed -e '1d' | while read line; do
  path=$(echo ${line} | awk '{print $1}')

  # skip any libraries that are /usr/lib or /System/Library; these are assumed to be part of the OS.
  # TODO: are there any additional paths that should be whitelisted?
  echo ${path} | grep -q -e '^\(/usr/lib\|/System/Library\)'
  status=$?

  if [ "${status}" == "0" ]; then
    continue;
  fi;

  base=$(basename ${path})
  new_path="${new_root}/${base}"

  echo "${path} -> ${new_path}"

  # determine if -id or -change should be used based on the filename's first
  # "token"; match the string up to the first dot.  If it matches the filename
  # then use -id.  For example, -id will be used for the reference
  # libpth.20.dylib in a file named libpth.20.0.27.dylib because "libpth"
  # matches both the filename and reference.
  if [ "$(echo ${base} | sed 's/\..*//')" == "$(echo ${dylib_base} | sed 's/\..*//')" ]; then
    install_name_tool -id "${new_path}" "${dylib}"
  else
    install_name_tool -change "${path}" "${new_path}" "${dylib}"
  fi;
done;

echo
otool -L ${dylib}
