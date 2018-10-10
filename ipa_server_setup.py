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

def ipa_stuff(name, domain):
    
    # create output array
    output = [0] * 2
    # try to run ipa-server-install
    try:
      output[0] = subprocess.check_output(["/sbin/ipa-server-install", "-p", "XXX", "-a", "XXXX", "--hostname=ipa1.example.com", "-n", "example.com", "-r", "example.com", "--forwarder=8.8.8.8", "--setup-dns", "-U"], stderr=subprocess.STDOUT)
      output[1] = 0
    # on error, return error and false
    except subprocess.CalledProcessError as e:
      output[0] = e.output
      output[1] = 1

    return output
    

def run_module():
    # define the available arguments/parameters that a user can pass to
    # the module
    module_args = dict(
        name=dict(type='str', required=True),
        domain=dict(type='str', required=False)
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
    output = ipa_stuff(module.params['name'], module.params['domain'])

    result['output'] = output[0]
    result['rc'] = output[1]

    if not output[1]:
      result['changed'] = True
      result['message'] = "Module Success!"

    else:
      result['message'] = "Module failed!"


    # during the execution of the module, if there is an exception or a
    # conditional state that effectively causes a failure, run
    # AnsibleModule.fail_json() to pass in the message and the result
    if module.params['name'] == 'fail me':
        module.fail_json(msg='You requested this to fail', **result)

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()
