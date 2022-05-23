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
import datetime
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
    """
    This method gets the list of packages in aggregate
    """
      
    # get the list of elements in aggregate
    dir_list = os.listdir(path)
  
    return dir_list

# get the path of a given recipe
def get_recipe_path(recipe):
    """
    This method finds the path of a given recipe
    """
    
    # get the current directory url
    current_path = current_directory()

    # get the recipe path
    path_of_recipe = "{0}/aggregate/{1}".format(current_path,recipe)

    return path_of_recipe

# display the list of recipes
def display_recipes(dir_list):
    """
    This method displays the list of recipes 
    """
   
    # print elements in the aggregate folder
    for recipe in dir_list:
         print(recipe)

         # get the recipe path
         #recipe_path = get_recipe_path(recipe)

         # display the meta.yaml
         meta_result = find_meta_yaml(recipe)
         
         # display the run_test
         sh_result, py_result, bat_result = find_run_test(recipe)

         #----
         print("---")
         print("Meta.yaml Exists? : {0}".format(meta_result))
         print("run_tests.sh Exists? : {0}".format(sh_result))
         print("run_tests.py Exists? : {0}".format(py_result))
         print("run_tests.bat Exists? : {0}".format(bat_result))
         print("------------------")

# find and open the meta.yaml
def find_meta_yaml(recipe):
    """
    This method verifies that the meta.yaml file is available in the recipe
    The input is as follows: <recipe-name>
    The output is as follows: <verify_meta_exists>
    """

    recipe_path = get_recipe_path(recipe)
    
    # declare variable
    recipe_location = "{0}/recipe/meta.yaml".format(recipe_path)    

    # verify that the meta.yaml file is available
    verify_meta_exists = os.path.isfile(recipe_location)

    return verify_meta_exists

# see if a test section is included in the meta.yaml

# check to see if the run_test file is available
def find_run_test(recipe):
    """
    This method verifies if the test_run files are included in the recipe
    The input is as follows: <recipe-name>
    The output is as follows: <sh_exists> <py_exists> <bat_exists>
    """

    # get the path of the recipe
    recipe_path = get_recipe_path(recipe)

    # declare variables
    run_test_sh = "{0}/recipe/run_test.sh".format(recipe_path) 
    run_test_py = "{0}/recipe/run_test.py".format(recipe_path) 
    run_test_bat = "{0}/recipe/run_test.bat".format(recipe_path)

    # verify that the runn_test file is available
    sh_exists = os.path.isfile(run_test_sh)
    py_exists = os.path.isfile(run_test_py)
    bat_exists = os.path.isfile(run_test_bat)

    return sh_exists, py_exists, bat_exists

# get packages with no test_run files
def missing_file(dir_list):

    # declare variables
    missing_file_count = 0
    recipe_result = []

    # loop to find the find the packages without test files
    for recipe in dir_list:
        # gather the run_test results
        sh_result, py_result, bat_result = find_run_test(recipe)

        # evaluate the test results
        if(sh_result is False and py_result is False and bat_result is False):
            print(recipe)
            print("sh: {0} | py: {1} | bat: {2}".format(sh_result, py_result, bat_result))
            print("No test files") 
            missing_file_count = missing_file_count + 1

        # update the recipe results
        recipe_result.append([recipe, sh_result, py_result, bat_result])
    
    # return the results
    return missing_file_count, recipe_result

# get packages with only one test_run file
def have_one_file(dir_list):
    
    # declare variables
    one_file_count = 0
    recipe_result = []

    # loop to find the packages containing one test file
    for recipe in dir_list:
        # gather the run_test results
        sh_result, py_result, bat_result = find_run_test(recipe)
        #print(recipe)
        #print("sh: {0} | py: {1} | bat: {2}".format(sh_result, py_result, bat_result))

        if((sh_result is True and py_result is False and bat_result is False) or 
        (sh_result is False and py_result is True and bat_result is False) or
        (sh_result is False and py_result is False and bat_result is True)): 
            print(recipe)
            print("sh: {0} | py: {1} | bat: {2}".format(sh_result, py_result, bat_result))
            print("one file") 
            one_file_count = one_file_count + 1

            # Update the recipe result
            recipe_result.append([recipe,sh_result,py_result,bat_result])

    return one_file_count, recipe_result

# get packages with two test_run files
def have_two_files(dir_list):
    
    # declare variables
    two_file_count = 0
    recipe_result = []

    # loop to find the files containing one file
    for recipe in dir_list:
        # gather the run_test results
        sh_result, py_result, bat_result = find_run_test(recipe)
        #print(recipe)
        #print("sh: {0} | py: {1} | bat: {2}".format(sh_result, py_result, bat_result))
        
        if((sh_result is True and py_result is True and bat_result is False) or 
        (sh_result is False and py_result is True and bat_result is True) or
        (sh_result is True and py_result is False and bat_result is True)):   
            print(recipe)
            print("sh: {0} | py: {1} | bat: {2}".format(sh_result, py_result, bat_result))
            print("two file") 
            two_file_count = two_file_count + 1

            # Update the recipe result
            recipe_result.append([recipe,sh_result,py_result,bat_result])
            
    return two_file_count, recipe_result

# get packages with three test_run files
def have_three_file(dir_list):
    
    # declare variables
    three_file_count = 0
    recipe_result = []

    # loop to find the files containing one file
    for recipe in dir_list:
        # gather the run_test results
        sh_result, py_result, bat_result = find_run_test(recipe)
        #print(recipe)
        #print("sh: {0} | py: {1} | bat: {2}".format(sh_result, py_result, bat_result))
        
        if(sh_result is True and py_result is True and bat_result is True):   
            print(recipe)
            print("sh: {0} | py: {1} | bat: {2}".format(sh_result, py_result, bat_result))
            print("three file") 
            three_file_count = three_file_count + 1

            # Update the recipe result
            recipe_result.append([recipe,sh_result,py_result,bat_result])
    
    # display the total number of packages with 3 files
    #print("Number of packages with three files: {0}".format(three_file_count))
            
    return three_file_count, recipe_result

def find_percentage(file_result, aggregate_size):
    
    # calculate persentages
    file_persentage = (float(file_result) / float(aggregate_size)) * 100

    return file_persentage

# generate report results
def generate_reports(dir_list):
    """
    This method generates the reports
    """

    # declare variables
    aggregate_size = len(dir_list)

    print("-- Generate Reports --")

    top_location = current_directory()
        
    # get the date parameters
    date = datetime.date.today()

    day_number = date.day
    month_name = date.strftime("%B")
    year_number = date.year

    # set the directories
    file_name = "Report_{0}_{1}_{2}.md".format(month_name, day_number, year_number)
    file_name_one = "One_file_{0}_{1}_{2}.md".format(month_name, day_number, year_number)
    file_name_two = "Two_file_{0}_{1}_{2}.md".format(month_name, day_number, year_number)
    file_name_three = "Three_file_{0}_{1}_{2}.md".format(month_name, day_number, year_number)
    child_dir = "Report"

    # print the folder directories
    print("--- Folder Directories ---")

    file_location = "{0}/{1}/".format(top_location,child_dir)
    #print(file_location)

    # verify that the path directory exists
    locationStatus = Path(file_location).exists()

    # Gather sumarry information
    missing_file_result, missinng_file_list = missing_file(dir_list)
    one_file_result, one_file_list = have_one_file(dir_list)
    two_file_result, two_file_list = have_two_files(dir_list)
    three_file_result, three_file_list = have_three_file(dir_list)

    # calculate persentages
    missing_file_persentage = find_percentage(missing_file_result, aggregate_size)
    one_file_persentage = find_percentage(one_file_result, aggregate_size)
    two_file_persentage = find_percentage(two_file_result, aggregate_size)
    three_file_persentage = find_percentage(three_file_result, aggregate_size)

    # if the folder structure is missing then it is created
    if(locationStatus is False):
        #os.mkdirs(file_location)
        # makedirs allow to create nested directories
        # https://stackoverflow.com/questions/273192/how-can-i-safely-create-a-nested-directory
        os.makedirs(file_location) 

    # set the report information
    space = "\n---\n\n"
    header = "# {0} {1} {2} {3}".format( month_name, day_number, year_number,space)

    body = "## Report"+space
    body = body + "## Packages With No Test Files"+space
    body = body + "Number of packages with no test files: {0} \n".format(missing_file_result) 
    body = body + "Percentage of packages with no test files: {0:8.2f}% {1}".format(missing_file_persentage, space)
    body = body + "## Packages With One Test"+space
    body = body + "Number of packages with one file: {0} \n".format(one_file_result)
    body = body + "Percentage of packages with one file: {0:8.2f}% {1}".format(one_file_persentage, space)
    body = body + "## Package With Two Test"+space
    body = body + "Number of packages with two files: {0} \n".format(two_file_result)
    body = body + "Percentage of packages with two files: {0:8.2f}% {1}".format(two_file_persentage, space)
    body = body + "## Package With Three Test"+space
    body = body + "Number of packages with three files: {0} \n".format(three_file_result, space)
    body = body + "Percentage of packages with three files: {0:8.2f}% {1}".format(three_file_persentage, space)

    reportTotal = header+body

    # write the file to the hardware
    with open(file_location + file_name,'w') as f:
        f.write(reportTotal)

    # report file with only one test file 
    
    # set the report information
    body = "## Report"+space
    
    # loop to add elements to file
    for one_file_package in one_file_list:

        # find the document existing
        if(one_file_package[1] is True):
            test_file_name = "test_run.sh"
        if(one_file_package[2] is True):
            test_file_name = "test_run.py"
        if(one_file_package[3] is True):
            test_file_name = "test_run.bat"

        body = body + "- `{0}` \n".format(one_file_package[0])
        body = body + "\t ({0}) \n".format(test_file_name)

    reportTotal = header+body

    with open(file_location + file_name_one,'w') as f:
        f.write(reportTotal)

    # report file with two test files

    # set the report information
    body = "## Report"+space

    # loop to add elements to file
    for two_file_package in two_file_list:

        # find the document existing
        if(two_file_package[1] is True and two_file_package[2] is True and two_file_package[3] is False):
            file_one_name = "test_run.sh"
            file_two_name = "test_run.py"
        if(two_file_package[1] is False and two_file_package[2] is True and two_file_package[3] is True):
            file_one_name = "test_run.py"
            file_two_name = "test_run.bat"
        if(two_file_package[1] is True and two_file_package[2] is False and two_file_package[3] is True):
            file_one_name = "test_run.sh"
            file_two_name = "test_run.bat"
    
        body = body + "- `{0}` \n".format(two_file_package[0])
        body = body + "\t ({0} {1}) \n".format(file_one_name, file_two_name)
    
    reportTotal = header+body

    with open(file_location + file_name_two,'w') as f:
        f.write(reportTotal)

    return False

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
        #display_recipes(recipes)

        # generate reports
        generate_reports(recipes)

        # -----------------------------------

        # debug the function for only one recipe
        #one_file_result = have_one_file(recipes)
        
        # print the result
        #print("Results for certifi-feedstock : {0}".format(one_file_result))

if __name__ == '__main__':
    sys.exit(main())
