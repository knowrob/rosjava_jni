#!/usr/bin/env python
# Software License Agreement (BSD License)
#
# Copyright (c) 2009, Willow Garage, Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following
#    disclaimer in the documentation and/or other materials provided
#    with the distribution.
#  * Neither the name of Willow Garage, Inc. nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#

## ROS message source code generation for C++
## 
## Converts ROS .msg files in a package into C++ source code implementations.

import roslib; roslib.load_manifest('rosjava_jni')
import genmsg_java
 
import sys
import os
import traceback

# roslib.msgs contains the utilities for parsing .msg specifications. It is meant to have no rospy-specific knowledge
import roslib.srvs
import roslib.packages
import roslib.gentools

from cStringIO import StringIO

def write_begin(s, spec, file):
    """
    Writes the beginning of the header file: a comment saying it's auto-generated and the include guards
    
    @param s: The stream to write to
    @type s: stream
    @param spec: The spec
    @type spec: roslib.srvs.SrvSpec
    @param file: The file this service is being generated for
    @type file: str 
    """
    s.write("/* Auto-generated by genmsg_cpp for file %s */\n"%(file))
    s.write('\npackage ros.pkg.%s.srv;\n' % spec.package)
    s.write('\nimport java.nio.ByteBuffer;\n')

def write_end(s, spec):
    """
    Writes the end of the header file: the ending of the include guards
    
    @param s: The stream to write to
    @type s: stream
    @param spec: The spec
    @type spec: roslib.srvs.SrvSpec
    """
    pass
    
def generate(srv_path, output_base_path=None):
    """
    Generate a service
    
    @param srv_path: the path to the .srv file
    @type srv_path: str
    """
    (package_dir, package) = roslib.packages.get_dir_pkg(srv_path)
    (_, spec) = roslib.srvs.load_from_file(srv_path, package)
    
    s = StringIO()  
    write_begin(s, spec, srv_path)
    s.write('\n')
    
    gendeps_dict = roslib.gentools.get_dependencies(spec, spec.package)
    md5sum = roslib.gentools.compute_md5(gendeps_dict)

    s.write("""
public class %(srv_name)s extends ros.communication.Service<%(srv_name)s.Request, %(srv_name)s.Response> {

  public static java.lang.String __s_getDataType() { return "%(srv_data_type)s"; }
  public static java.lang.String __s_getMD5Sum() { return "%(srv_md5sum)s"; }

  public java.lang.String getDataType() { return %(srv_name)s.__s_getDataType(); }
  public java.lang.String getMD5Sum() { return %(srv_name)s.__s_getMD5Sum(); }

  public %(srv_name)s.Request createRequest() {
    return new %(srv_name)s.Request();
  }

  public %(srv_name)s.Response createResponse() {
    return new %(srv_name)s.Response();
  }

""" % {'srv_name': spec.short_name,
       'srv_data_type': spec.full_name,
       'srv_md5sum': md5sum})

    request_data_type = '"%s/%s"' % (spec.package, spec.request.short_name)
    response_data_type = '"%s/%s"' % (spec.package, spec.response.short_name)
    spec.request.short_name = 'Request'
    spec.response.short_name = 'Response'
    genmsg_java.write_class(s, spec.request, {'ServerMD5Sum': '"%s"' % md5sum,
                                              'DataType': request_data_type}, True)
    s.write('\n')
    genmsg_java.write_class(s, spec.response, {'ServerMD5Sum': '"%s"' % md5sum,
                                               'DataType': response_data_type}, True)
    s.write('\n} //class\n')
    
    write_end(s, spec)

    if output_base_path:
        output_dir = '%s/ros/pkg/%s/srv'%(output_base_path, package)
    else:
        output_dir = '%s/srv_gen/java/ros/pkg/%s/srv'%(package_dir, package)

    if (not os.path.exists(output_dir)):
        # if we're being run concurrently, the above test can report false but os.makedirs can still fail if
        # another copy just created the directory
        try:
            os.makedirs(output_dir)
        except OSError, e:
            pass
        
    f = open('%s/%s.java'%(output_dir, spec.short_name), 'w')
    print >> f, s.getvalue()
    
    s.close()

def generate_services(argv):
    if not os.path.exists(argv[-1]) or os.path.isdir(argv[-1]):
        for arg in argv[1:-1]:
            generate(arg, argv[-1])
    else:
        for arg in argv[1:]:
            generate(arg)

if __name__ == "__main__":
    roslib.msgs.set_verbose(False)
    generate_services(sys.argv)
    
