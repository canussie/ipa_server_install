#!/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '1.0',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: ipa_server_install 

short_description: Setup an ipa_server

version_added: "2.4"

description:
    - "After installing the ipa-server package, use this module to ipa-server configured and running"

options:

extends_documentation_fragment:
    - ipa-server 

author:
    - Ben Lewis
'''

EXAMPLES = '''
# Pass in a message
- name: Test with a message
  my_new_test_module:
    name: hello world

# pass in a message and have changed true
- name: Test with a message and changed output
  my_new_test_module:
    name: hello world
    new: true

# fail the module
- name: Test failure of the module
  my_new_test_module:
    name: fail me
'''

RETURN = '''
original_message:
    description: The original name param that was passed in
    type: str
message:
    description: The output message that the sample module generates
'''

from ansible.module_utils.basic import AnsibleModule
import os
import subprocess
import re

def ipa_stuff(params):
  #
  # get parameters from args dict
  #
  ipahostname = "--hostname=" + params["hostname"]
  adminpass = params["adminpass"]
  dmpass = params["dmpass"]
  domainname = params["domainname"]
  realmname = params["realmname"]
  # define output dict with some sane defaults
  results = {
    "output": "",
    "rc": "0",
    "change": True,
  }
  # 
  # attempt to run the IPA install 
  #
  try:
    #
    # set the values to reflect a successful run
    #
    results["output"] = subprocess.check_output(["/sbin/ipa-server-install", "-p", dmpass, "-a", adminpass, ipahostname, "-n", domainname, "-r", realmname, "--forwarder=8.8.8.8", "--setup-dns", "-U"], stderr=subprocess.STDOUT)
    results["rc"] = 0
    results["change"] = True
  #
  # catch any exceptions 
  #
  except subprocess.CalledProcessError as e:
    #
    # place the error in the dict, set change to false and change return code to error (1)
    #
    results["output"] = e.output
    results["change"] = False
    results["rc"] = 1
    #
    # split the command output by newline
    #
    search_output = results["output"].split('\n')
    #
    # iterate through array
    #
    for x in search_output:
      #
      # check if error is due to ipa already being configured
      #
      regexpgroup = re.search('^.*already exists in DNS.*(server\(s\))\:\s(.+)\.$', x)
      #
      # if failure is due to zone already being managed by a DNS master do some more checks
      #
      if regexpgroup:
        # 
        # check hostname of ipa server
        #
        hostname = subprocess.check_output("hostname").rstrip()
        #print "Found something"
        #
        # get DNS server name hosting zone requested
        #
        dnshost = regexpgroup.group(2).rstrip()
        #print dnshost
        #print hostname
        #
        # if hostnames match, change error to a non failure for idempotent
        #
        if hostname == dnshost:
          results["output"] = "IPA already configured on server."
          results["rc"] = 0
          results["change"] = False
  #
  # return result dict 
  #
  return results
      
  
def run_module():
    # define the available arguments/parameters that a user can pass to
    # the module
    module_args = dict(
        hostname=dict(type='str', required=True),
        adminpass=dict(type='str', required=True),
        dmpass=dict(type='str', required=True),
        domainname=dict(type='str', required=True),
        realmname=dict(type='str', required=True)
    )

    # seed the result dict in the object
    # we primarily care about changed and state
    # change is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(
        changed=False,
        message=''
    )

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    if module.check_mode:
        return result

    # manipulate or modify the state as needed (this is going to be the
    # part where your module will do what it needs to do)
    #result['message'] = 'goodbye'

    # if domain specified
    #if module.params['domain']:
    #  result['changed'] = True
    ipa_params = {
      "hostname": module.params["hostname"],
      "adminpass": module.params["adminpass"],
      "dmpass": module.params["dmpass"],
      "domainname": module.params["domainname"],
      "realmname": module.params["realmname"]
    }

    joinstate = ipa_stuff(ipa_params)

    result['message'] = joinstate["output"]
    result['rc'] = joinstate["rc"]
    result['changed'] = joinstate["change"]

    # during the execution of the module, if there is an exception or a
    # conditional state that effectively causes a failure, run
    # AnsibleModule.fail_json() to pass in the message and the result
    if module.params['hostname'] == 'fail me':
        module.fail_json(msg='You requested this to fail', **result)

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()
