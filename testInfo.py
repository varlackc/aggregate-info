#!/usr/bin/env python3

#######################################################
# This script looks for the packages in aggregate     #
# Outputs relevant information regarding the package  #
# tests                                               #
#                                                     #
#######################################################

import argparse
import os
from os import lseek, system, chdir
import os.path
import sys
import pathlib
from pathlib import Path

__path__ = '.'
__author__ = 'Maxwell Varlack'
__version__ = '0.0.1'

path = 'aggregate'

def argument_parsing(parse=None):
    parser = argparse.ArgumentParser(description='Character Counting Program')
    parser.add_argument('-i', '--input', type=str, metavar='', required=True, help='Input File')
    args, unknown = parser.parse_known_args()
    return args, unknown

# search to see if the aggregate folder is available
def aggregate_available(current_dir):
    """ 
    this method confirms is aggregate is available
    """

    # format the expected path of the aggregate folder
    aggregate_path = "{0}/aggregate".format(current_dir)

    # verify if the folder exists in the expected path
    verify_aggregate = os.path.isdir(aggregate_path)

    return verify_aggregate
    
# get the current directory of the current location
def current_directory():
    """
    This method verifies the location of the current directory
    """

    # source code of the Path.absolute function used to get the absolute path
    # https://github.com/python/cpython/blob/3.8/Lib/pathlib.py#L1155&&L1172
    # present_directory = Path.absolute()
    present_directory = os.getcwd()

    return present_directory
    
# get a list of the folders inside of aggregate
def get_list_packages():
      
      # get the list of elements in aggregate
      dir_list = os.listdir(path)
  
      return dir_list

# display the list of recipes
def display_recipes(dir_list):
   
     # get the current directory url
     current_path = current_directory()
 
     # print elements in the aggregate folder
     for recipe in dir_list:
         print(recipe)

         # get the recipe url
         recipe_path = "{0}/aggregate/{1}".format(current_path,recipe)
         print(recipe_path)

         # display the meta.yaml
         find_meta_yaml(recipe_path)
         
         # display the run_test
         find_run_test(recipe_path)

# find and open the meta.yaml
def find_meta_yaml(recipe):
    
    # declare variable
    recipe_location = "{0}/recipe/meta.yaml".format(recipe)    

    # Print element 
    #print(recipe_location)

    # verify that the meta.yaml file is available
    verify_meta_exists = os.path.isfile(recipe_location)

    print("Does Meta.yaml Exists? : {0}".format(verify_meta_exists))

    return verify_meta_exists

# see if a test section is included in the meta.yaml

# check to see if the run_test file is available
def find_run_test(recipe):
    """
    This method verifies if the test_run files are included in the recipe
    """

    # declare variables
    run_test_sh = "{0}/recipe/run_test.sh".format(recipe) 
    run_test_py = "{0}/recipe/run_test.sh".format(recipe) 
    run_test_bat = "{0}/recipe/run_test.sh".format(recipe)

    # Print element
    #print(recipe_location)

    # verify that the runn_test file is available
    sh_exists = os.path.isfile(run_test_sh)
    py_exists = os.path.isfile(run_test_py)
    bat_exists = os.path.isfile(run_test_bat)


    print("Does run_test.sh Exists? : {0}".format(sh_exists))
    print("Does run_test.py Exists? : {0}".format(py_exists))
    print("Does run_test.bat Exists? : {0}".format(bat_exists))

#def main(args=None, unknown=None):
def main():
    """
    This Method verifies the quality of the existing tests
    in aggregate.
    """
    
    # Verify the current location
    directory_location = current_directory()
    # direcory_location = Path.absolute()

    # Verify if aggregate is available
    aggregate_available_result = aggregate_available(directory_location)
    
    # if aggregate is not available inform the user
    if (aggregate_available_result is False):
        print("Aggregate is not available")

    # if aggregate is available continue to gather information on aggregate tests    
    else:
        # get the feedstocks in aggregate
        recipes = get_list_packages()
    
        # display the list of existing recipes
        display_recipes(recipes)


if __name__ == '__main__':
    sys.exit(main())
