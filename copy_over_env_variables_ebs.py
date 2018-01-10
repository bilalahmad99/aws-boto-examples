### HOw to Run it #####
#It copy ENV variables from source to destination

#python copy_over_env_variables_ebs.py --help
"""
Usage: copy_over_env_variables_ebs.py [options] filename

Options:
--version             show program's version number and exit
-h, --help            show this help message and exit
--profileSource=PROFILESOURCE
Source AWS Profile
--ebsAppSource=EBSAPPSOURCE
source Ebs App
--ebsEnvSource=EBSENVSOURCE
source EBS ENV
--profileTarget=PROFILETARGET
Target AWS Profile
--ebsAppTarget=EBSAPPTARGET
Target Ebs App
--ebsEnvTarget=EBSENVTARGET
Target EBS ENV

Example  -

python copy_over_env_variables_ebs.py --profileSource stage_aws_account --ebsAppSource app --ebsEnvSource app-env --profileTarget test_aws_account --ebsAppTarget app1 --ebsEnvTarget app1-env1

"""

import boto3
class BeanStalk(object):

    """
    Example usage
    boto_profile = ""
    beanstalk_application_name = ""
    beanstalk_environment_name = ""
    return BeanStalk(profile=boto_profile,
                     application=beanstalk_application_name,
                     environment=beanstalk_environment_name).environment_detail()
    Class to fetch data from AWS Beanstalk environment
    Scope of this class if not to create new application
    or environment in any already created application.
    However, we will update environments and to be specific
    just the the environment variables of environments.
    """
    def __init__(self, profile=None,
                 application=None,
                 environment=None):
        self.profile = profile
        self.application = application
        self.environment = environment
        self.session = boto3.Session(profile_name=self.profile)
        try:
            self.client = self.session.client("elasticbeanstalk")
        except Exception, e:
            self.client = None
            print(e)

    def application_detail(self):
        """
        Get details of the given application.
        Most probably we will not use this, but
        just in case if we need this
        :return: app_detail: type dict
        """
        if self.client and self.application:
            try:
                response_beanstalk = self.client.describe_applications()['Applications']
            except Exception, e:
                print(e)
                return {}
            else:
                return response_beanstalk

    def environment_detail(self):
        """
        Get details of the given environment
        Here we do not rely on the application, however
        the environment name you provide should be under
        the application name provided.
        The reason we will not rely on application is because
        the application can have multiple environments
        and each environment can have separate environment
        variables.
        Be very specific when providing environment name
        :return: env_var_dict: type dict
        """
        if self.client and self.application and self.environment:
            env_var_dict = {}
            try:
                env_details = self.client.describe_configuration_settings(
                    ApplicationName=self.application,
                    EnvironmentName=self.environment
                )
            except Exception, e:
                env_var_dict = {}
                print(e)
                exit()
            else:

                env_vars = [
                    z for z in env_details[
                        'ConfigurationSettings'
                    ][0]['OptionSettings'] if z['Namespace'] == 'aws:elasticbeanstalk:application:environment'
                ]
                return env_vars

            ## NOt Doing below, as we dont need it.
            current_key = None
            try:
                for item in env_vars:
                    if '=' in item:
                        current_key, value = item.split('=',1)
                        # This puts a string as the value
                        env_var_dict[current_key] = value
                    else:
                        # Check if the value is already a list
                        if not isinstance(env_var_dict[current_key], list):
                            # If value is not a list, create one
                            env_var_dict[current_key] = [env_var_dict[current_key]]
                        env_var_dict[current_key].append(item)
            except IndexError:
                pass
            else:
                #return env_string
                return env_var_dict

    def update_environment_variables(self, env_vars):
        """
        Get details of the given environment
        Here we do not rely on the application, however
        the environment name you provide should be under
        the application name provided.
        The reason we will not rely on application is because
        the application can have multiple environments
        and each environment can have separate environment
        variables.
        Be very specific when providing environment name
        :return: env_var_dict: type dict
        """
        if self.client and self.application and self.environment:
            #option_settings_env_dict['Value'] = env_string
            try:
                env_details = self.client.update_environment(
                    ApplicationName=self.application,
                    EnvironmentName=self.environment,
                    OptionSettings=env_vars
                )
            except Exception, e:
                print("Exception while updating the destination Elastic Benastalk Endpoint")
                print(e)
                exit()



from optparse import OptionParser

def main():
    parser = OptionParser(usage="usage: %prog [options] filename",
                          version="%prog 1.0")
    parser.add_option("--profileSource",
                      dest="profileSource",
                      default=False,
                      help="Source AWS Profile")
    parser.add_option("--ebsAppSource",
                      dest="ebsAppSource",
                      default=False,
                      help="source Ebs App")
    parser.add_option("--ebsEnvSource",
                      dest="ebsEnvSource",
                      default=False,
                      help="source EBS ENV")

    parser.add_option("--profileTarget",
                      dest="profileTarget",
                      default=False,
                      help="Target AWS Profile")
    parser.add_option("--ebsAppTarget",
                      dest="ebsAppTarget",
                      default=False,
                      help="Target Ebs App")
    parser.add_option("--ebsEnvTarget",
                      dest="ebsEnvTarget",
                      default=False,
                      help="Target EBS ENV")

    (options, args) = parser.parse_args()
    print options

    ebs_source_object = BeanStalk(options.profileSource, options.ebsAppSource, options.ebsEnvSource)
    env_string = ebs_source_object.environment_detail()
    print "Source app environment variables ====  %s" % env_string

    ebs_dest_object = BeanStalk(options.profileTarget, options.ebsAppTarget, options.ebsEnvTarget)
    ebs_dest_object.update_environment_variables(env_string)
    print "Destination  app environment variables ===="

if __name__ == '__main__':
    main()
