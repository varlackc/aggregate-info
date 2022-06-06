#! /usr/bin/env python3

#######################################################
# This script looks for the packages in aggregate     #
# Outputs relevant information regarding the package  #
# tests                                               #
#                                                     #
# The package makes use of pyyaml to gather meta.yaml #
# data from the recipes in aggregate.                 #
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
# need to install pyyaml before using the pyyaml package
import yaml
# standard python library used for file operations such as copying files
# https://docs.python.org/3/library/shutil.html
import shutil
# the fileinput standard library module
# will be used to replace content in file
# https://docs.python.org/3/library/fileinput.html
import fileinput
# jinja2 will be used to render the meta.yaml templates into usable yaml files
# https://jinja2docs.readthedocs.io/_/downloads/en/stable/pdf/
import jinja2
from jinja2 import Environment, FileSystemLoader

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
            #print(recipe)
            #print("sh: {0} | py: {1} | bat: {2}".format(sh_result, py_result, bat_result))
            #print("No test files") 
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
            #print(recipe)
            #print("sh: {0} | py: {1} | bat: {2}".format(sh_result, py_result, bat_result))
            #print("one file") 
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
            #print(recipe)
            #print("sh: {0} | py: {1} | bat: {2}".format(sh_result, py_result, bat_result))
            #print("two file") 
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
            #print(recipe)
            #print("sh: {0} | py: {1} | bat: {2}".format(sh_result, py_result, bat_result))
            #print("three file") 
            three_file_count = three_file_count + 1

            # Update the recipe result
            recipe_result.append([recipe,sh_result,py_result,bat_result])
    
    # display the total number of packages with 3 files
    #print("Number of packages with three files: {0}".format(three_file_count))
            
    return three_file_count, recipe_result

# calculate percentages
def find_percentage(file_result, aggregate_size):
    
    # calculate persentages
    file_persentage = (float(file_result) / float(aggregate_size)) * 100

    return file_persentage

# create temporary files
def generate_temporary_file(recipe_name):
    
    #print("Generate Temporary File")
    #print("----------------------------")

    # declare variables
    child_dir = "Temp"
    top_location = current_directory()
    file_location = "{0}/{1}/".format(top_location,child_dir)

    # verify that the Temporary folder exists
    locationStatus = Path(file_location).exists()    

    # if the folder structure is missing then it is created
    if(locationStatus is False):
        #os.mkdirs(file_location)
        # makedirs allow to create nested directories
        # https://stackoverflow.com/questions/273192/how-can-i-safely-create-a-nested-directory
        os.makedirs(file_location) 

    #print("child_dir: {0}".format(child_dir))
    #print("top_location: {0}".format(top_location))
    #print("file_location: {0}".format(file_location))
    #print("locationStatus: {0}".format(locationStatus))
    #print("----------------------------")

    # declare the location of the recipe
    recipe_location = "{0}/aggregate/{1}".format(top_location,recipe_name)
    meta_location = "{0}/aggregate/{1}/recipe/meta.yaml".format(top_location,recipe_name)

    # verify that the location exists
    recipeLocationStatus = Path(recipe_location).exists()
    #recipeLocationStatus = Path.exists(recipe_location)
    #print(recipeLocationStatus)
    metaLocationStatus = Path(meta_location).exists()

    # need to verify if the file exists not just the folder

    # if the folder location exists then copy the files
    #if(recipeLocationStatus is True):
    if(metaLocationStatus is True):
        
        # set meta.yaml location 
        file_to_copy = "{0}/recipe/meta.yaml".format(recipe_location)

        #print("----------------------------")
        #print("recipe_location: {0}".format(recipe_location))
        #print("file_to_copy: {0}".format(file_to_copy))
        #print("destination: {0}".format(file_location))
        #print("recipeLocationStatus: {0}".format(recipeLocationStatus))
        #print("----------------------------")

        # copy the meta.yaml file to the temporary folder 
        # https://docs.python.org/3/library/shutil.html
        shutil.copy2(file_to_copy,file_location)

    else:
        print("Could Not Locate The Recipe {0}".format(recipe_name))
        print("child_dir: {0}".format(child_dir))
        print("top_location: {0}".format(top_location))
        print("file_location: {0}".format(file_location))
        print("recipe_location: {0}".format(recipe_location))
        print("recipe_name: {0}".format(recipe_name))
        print("recipeLocationStatus: {0}".format(recipeLocationStatus))
        print("meta location: {0}".format(meta_location))
        print("metaLocationStatus: {0}".format(metaLocationStatus))

    # write the file 
#    with open(file_location + temp_file_name, 'w') as f:
#        f.write(data)


    # copy the file to the new location
    #shutil.copy2(source_file,file_location)

    pass

# render meta jinja templates
def render_meta_file(recipe):
    
    # declare variables
    template_folder = 'Temp'
    template_name = 'meta.yaml'
    file_to_render = "Temp/meta.yaml"
    configurations = {"compiler":"compiler","compiler('c')":"c_compiler", "cdt":"cdt",
    "pin_subpackage":"pin", "os":"os", "environ":"environment","libgomp_ver":"libgomp_ver",
    "pin_compatible":"pin_compatible"}

    loader = FileSystemLoader(template_folder)
    env = Environment(loader = loader)
    template = env.get_template(template_name)
    result = template.render(configurations)
    with open(file_to_render, 'w') as meta:
        meta.write(result)
    pass

def replace_template(temp_file, line_to_modify, line_to_replace):
    # replace the lines in the meta.yaml that are used for the jinja2 template
    for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
        # replace the jinja2 template sections
        sys.stdout.write(line.replace(line_to_modify,line_to_replace))
    pass

# modify the temporary file to make the meta file compatible with pyyaml
def modify_temporary_file(recipe_name):
    """
    This file modifies the temporary file to make it easier to parse
    """
    print("Recipe_Name: {0}".format(recipe_name))
    # declare variables
    line_to_modify = "{%"
    line_to_replace = "#{%"
    modify_script = "script:"
    replace_script = "#script:"
    modify_script2 = "script:\n"
    replace_script2 = "#script:\n#"
    modify_name = "name: {{"
    replace_name = "#name: {{"
    modify_version = "version: {{"
    replace_version = "#version: {{"
    modify_template = "- {{ "
    replace_template = "#- {{ "
    modify_url = "https://www.googleapis.com/"
    replace_url = "# https://www.googleapis.com/"
    modify_fn = "fn: {{ "
    replace_fn = "#fn: {{ "
    modify_sha256 = "sha256: {{ "
    replace_sha256 = "#sha256: {{ "
    modify_template2 = "  {{ "
    replace_template2 = "  #{{ "
    modify_number = "number: {{ "
    replace_number = "#number: {{"
#    modify_number2 = "number: "
#    replace_number2 = "#number: "
    modify_compiler = "- {{ compiler('c')"
    replace_compiler = "- {{ c_compiler"
    modify_compiler2 = '- {{ compiler("c")'
    replace_compiler2 = "- {{ c_compiler"
    modify_compiler3 = "- {{ compiler('cxx')"
    replace_compiler3 = "- {{ cxx_compiler"
    modify_compiler4 = '- {{ compiler("cxx")'
    replace_compiler4 = "- {{ cxx_compiler"
    modify_compiler5 = "- {{ compiler('fortran')"
    replace_compiler5 = "- {{ fortran_compiler"
    modify_compiler6 = '- {{ compiler("cuda")'
    replace_compiler6 = "- {{ cuda_compiler"

    modify_runtime = " ~ '_runtime'"
    replace_runtime = ""
    modify_runtime2 = " ~ runtime_year"
    replace_runtime2 = ""


    modify_cdt = "- {{ cdt('xorg-x11-proto-devel')"
    replace_cdt = "- {{ cdt"
    modify_cdt2 = "- {{ cdt('libx11-devel')"
    replace_cdt2 = "- {{ cdt"
    modify_cdt3 = "- {{ cdt('libxext-devel')"
    replace_cdt3 = "- {{ cdt"
    modify_cdt4 = "- {{ cdt('libxrender-devel')"
    replace_cdt4 = "- {{ cdt"
    modify_cdt5 = "- {{ cdt('mesa-libgl-devel')"
    replace_cdt5 = "- {{ cdt"
    modify_cdt6 = "- {{ cdt('mesa-libegl-devel')"
    replace_cdt6 = "- {{ cdt"
    modify_cdt7 = "- {{ cdt('mesa-dri-drivers')"
    replace_cdt7 = "- {{ cdt" 
    modify_cdt8 = "- {{ cdt('libxau-devel')"
    replace_cdt8 = "- {{ cdt" 
    modify_cdt9 = "- {{ cdt('alsa-lib-devel')"
    replace_cdt9 = "- {{ cdt" 
    modify_cdt10 = "- {{ cdt('gtk2-devel')"
    replace_cdt10 = "- {{ cdt" 
    modify_cdt11 = "- {{ cdt('gtkmm24-devel')"
    replace_cdt11 = "- {{ cdt" 
    modify_cdt12 = "- {{ cdt('libdrm-devel')"
    replace_cdt12 = "- {{ cdt" 
    modify_cdt13 = "- {{ cdt('libxcomposite-devel')"
    replace_cdt13 = "- {{ cdt" 
    modify_cdt14 = "- {{ cdt('libxcursor-devel')" 
    replace_cdt14 = "- {{ cdt"
    modify_cdt15 = "- {{ cdt('libxi-devel')" 
    replace_cdt15 = "- {{ cdt"
    modify_cdt16 = "- {{ cdt('libxrandr-devel')"
    replace_cdt16 = "- {{ cdt" 
    modify_cdt17 = "- {{ cdt('pciutils-devel')"
    replace_cdt17 = "- {{ cdt" 
    modify_cdt18 = "- {{ cdt('libxscrnsaver-devel')"
    replace_cdt18 = "- {{ cdt" 
    modify_cdt19 = "- {{ cdt('libxtst-devel')"
    replace_cdt19 = "- {{ cdt" 
    modify_cdt20 = "- {{ cdt('libselinux-devel')"
    replace_cdt20 = "- {{ cdt" 
    modify_cdt21 = "- {{ cdt('libxdamage')"
    replace_cdt21 = "- {{ cdt" 
    modify_cdt22 = "- {{ cdt('libxfixes')"
    replace_cdt22 = "- {{ cdt" 
    modify_cdt23 = "- {{ cdt('libxxf86vm')"
    replace_cdt23 = "- {{ cdt"
    modify_cdt24 = "- {{ cdt('libselinux')"
    replace_cdt24 = "- {{ cdt"
    modify_cdt25 = "- {{ cdt('libxfixes-devel')"
    replace_cdt25 = "- {{ cdt"
    modify_cdt26 = "- {{ cdt('libxcb')"
    replace_cdt26 = "- {{ cdt"
    modify_cdt27 = "- {{ cdt('libxdamage-devel')"
    replace_cdt27 = "- {{ cdt"
    modify_cdt28 = "- {{ cdt('libxau')"
    replace_cdt28 = "- {{ cdt"
    modify_cdt29 = "- {{ "
    replace_cdt29 = "- {{ cdt"
    modify_cdt30 = "- {{ "
    replace_cdt30 = "- {{ cdt"
    
    
    modify_min_pin = ", min_pin='x'"
    replace_min_pin = ""
    modify_min_pin2 = ', min_pin="x"'
    replace_min_pin2 = ""   
    modify_min_pin3 = ", min_pin='x.x'"
    replace_min_pin3 = ""   
    modify_min_pin4 = ', min_pin="x.x"'
    replace_min_pin4 = ""   
    modify_min_pin5 = ", min_pin='x.x.x'"
    replace_min_pin5 = ""   
    modify_min_pin6 = ', min_pin="x.x.x"'
    replace_min_pin6 = ""   
     
    modify_max_pin = ", max_pin=None"
    replace_max_pin = ""
    modify_max_pin2 = ", max_pin='x'"
    replace_max_pin2 = ""
    modify_max_pin3 = ', max_pin="x"'
    replace_max_pin3 = ""
    modify_max_pin4 = ", max_pin='x.x'"
    replace_max_pin4 = ""
    modify_max_pin5 = ', max_pin="x.x"'
    replace_max_pin5 = ""
    modify_max_pin6 = ', max_pin="x.x.x"'
    replace_max_pin6 = ""
    modify_max_pin7 = ", max_pin='x.x.x'"
    replace_max_pin7 = ""
    modify_max_pin8 = ', max_pin="x.x.x.x"'
    replace_max_pin8 = ""
    
    modify_exact = ", exact=True"
    replace_exact = ""
        
    modify_target_platform = " ~ ctng_target_platform"
    replace_target_platform = ""  

    modify_pin = "- {{ pin_subpackage('vc')"
    replace_pin = "- {{ pin"
    modify_pin2 = "- {{ pin_subpackage('vs' + runtime_year + '_runtime') "
    replace_pin2 = "- {{ pin"
    modify_pin3 = "- {{ pin_subpackage('vs')"
    replace_pin3 = "- {{ pin"
    modify_pin4 = "- {{ pin_subpackage('libpcap')"
    replace_pin4 = "- {{ pin"    
    modify_pin5 = "- {{ pin_subpackage('metis')"
    replace_pin5 = "- {{ pin"    
    modify_pin6 = "- {{ pin_subpackage('poppler')"
    replace_pin6 = "- {{ pin"
    modify_pin7 = "- {{ pin_subpackage('gl2ps')"
    replace_pin7 = "- {{ pin"  
    modify_pin8 = "- {{ pin_subpackage('at-spi2-core')"
    replace_pin8 = "- {{ pin"  
    modify_pin9 = "- {{ pin_subpackage('libevent')"
    replace_pin9 = "- {{ pin"  
    modify_pin10 = "- {{ pin_subpackage('h2o')"
    replace_pin10 = "- {{ pin"  
    modify_pin11 = "- {{ pin_compatible('numpy')"
    replace_pin11 = "- {{ pin"  
    modify_pin12 = "- {{ pin_subpackage('libuv')"
    replace_pin12 = "- {{ pin"
    modify_pin13 = '- {{ pin_subpackage("binutils_")'
    replace_pin13 = "- {{ pin"  
    modify_pin14 = '- {{ pin_subpackage("gcc-osize_")'
    replace_pin14 = "- {{ pin"  
    modify_pin15 = '- {{ pin_compatible("libgfortran-ng")'
    replace_pin15 = "- {{ pin"  
    modify_pin16 = "- {{ pin_subpackage('ffmpeg')"
    replace_pin16 = "- {{ pin"  
    modify_pin17 = "- {{ pin_subpackage('geoviews-core')"
    replace_pin17 = "- {{ pin"  
    modify_pin18 = "- {{ pin_subpackage('py-lief')"
    replace_pin18 = "- {{ pin"  
    modify_pin19 = "- {{ pin_subpackage('liblief')"
    replace_pin19 = "- {{ pin"  
    modify_pin20 = "- {{ pin_subpackage('freetype')"
    replace_pin20 = "- {{ pin"  
    modify_pin21 = "- {{ pin_subpackage('pango')"
    replace_pin21 = "- {{ pin"  
    modify_pin22 = "- {{ pin_subpackage('covid-sim-data')"
    replace_pin22 = "- {{ pin"  
    modify_pin23 = "- {{ pin_subpackage('libarchive')"
    replace_pin23 = "- {{ pin"
    modify_pin24 = "- {{ pin_subpackage('freetds')"
    replace_pin24 = "- {{ pin"
    modify_pin25 = "- {{ pin_subpackage('scotch')"
    replace_pin25 = "- {{ pin"
    modify_pin26 = "- {{ pin_subpackage('ptscotch')"
    replace_pin26 = "- {{ pin"
    modify_pin27 = '- {{ pin_compatible("numpy")'
    replace_pin27 = "- {{ pin"
    modify_pin28 = "- {{ pin_subpackage('libspatialite')"
    replace_pin28 = "- {{ pin"
    modify_pin29 = "- {{ pin_compatible('mkl-dnn')"
    replace_pin29 = "- {{ pin"
    modify_pin30 = "- {{ pin_compatible('intel-openmp')"
    replace_pin30 = "- {{ pin"
    modify_pin31 = "- {{ pin_subpackage('libmxnet')"
    replace_pin31 = "- {{ pin"
    modify_pin32 = "- {{ pin_subpackage('py-mxnet')"
    replace_pin32 = "- {{ pin"
    modify_pin33 = "- {{ pin_compatible('curl')"
    replace_pin33 = "- {{ pin"
    modify_pin34 = "- {{ pin_subpackage('numpy-base')"
    replace_pin34 = "- {{ pin"
    modify_pin35 = "- {{ pin_subpackage('libmagic')"
    replace_pin35 = "- {{ pin"
    modify_pin36 = '- {{ pin_subpackage("libgomp")'
    replace_pin36 = "- {{ pin"
    modify_pin37 = '- {{ pin_subpackage("libstdcxx-ng")'
    replace_pin37 = "- {{ pin"
    modify_pin38 = '- {{ pin_subpackage("libgfortran" ~ libgfortran_soname)'
    replace_pin38 = "- {{ pin"
    modify_pin39 = '- {{ pin_subpackage("libgfortran")'
    replace_pin39 = "- {{ pin"
    modify_pin40 = '- {{ pin_subpackage("binutils_impl_")'
    replace_pin40 = "- {{ pin"
    modify_pin41 = '- {{ pin_subpackage("libgcc-devel_")'
    replace_pin41 = "- {{ pin"
    modify_pin42 = '- {{ pin_subpackage("libgcc-ng")'
    replace_pin42 = "- {{ pin"
    modify_pin43 = '- {{ pin_subpackage("gcc_impl_")'
    replace_pin43 = "- {{ pin"
    modify_pin44 = '- {{ pin_subpackage("libstdcxx-devel_")'
    replace_pin44 = "- {{ pin"
    modify_pin45 = "- {{ pin_subpackage('_openmp_mutex')"
    replace_pin45 = "- {{ pin"
    modify_pin46 = '- {{ pin_subpackage("_openmp_mutex")'
    replace_pin46 = "- {{ pin"
    modify_pin47 = "- {{ pin_subpackage('libgomp')"
    replace_pin47 = "- {{ pin"
    modify_pin48 = "- {{ pin_subpackage('g2clib')"
    replace_pin48 = "- {{ pin"
    modify_pin49 = "- {{ pin_subpackage('libcurl')"
    replace_pin49 = "- {{ pin"
    modify_pin50 = "- {{ pin_compatible('cudatoolkit')"
    replace_pin50 = "- {{ pin"
    modify_pin51 = "- {{ pin_subpackage('libsodium')"
    replace_pin51 = "- {{ pin"
    modify_pin52 = "- {{ pin_subpackage('libtiff')"
    replace_pin52 = "- {{ pin"       
    modify_pin53 = '- {{ pin_subpackage("libdb")'
    replace_pin53 = "- {{ pin"
    modify_pin54 = "- {{ pin_subpackage('libdb')"
    replace_pin54 = "- {{ pin"
    modify_pin55 = '- {{ pin_subpackage(name)'
    replace_pin55 = "- {{ pin"
    modify_pin56 = '- {{ pin_subpackage("msvc-headers-libs")'
    replace_pin56 = "- {{ pin"
    modify_pin57 = '- {{ pin_subpackage("winsdk")'
    replace_pin57 = "- {{ pin"
    modify_pin58 = '- {{ pin_subpackage("libgit2")'
    replace_pin58 = "- {{ pin"
    modify_pin59 = "- {{ pin_subpackage('intel-cmplr-lic-rt')"
    replace_pin59 = "- {{ pin"
    modify_pin60 = "- {{ pin_subpackage('intel-cmplr-lib-rt')"
    replace_pin60 = "- {{ pin"
    modify_pin61 = "- {{ pin_subpackage('intel-opencl-rt')"
    replace_pin61 = "- {{ pin"
    modify_pin62 = "- {{ pin_subpackage('dpcpp-cpp-rt')"
    replace_pin62 = "- {{ pin"
    modify_pin63 = '- {{ pin_subpackage("dpcpp-cpp-rt")'
    replace_pin63 = "- {{ pin"
    modify_pin64 = "- {{ pin_subpackage('dpcpp_impl_linux-64')"
    replace_pin64 = "- {{ pin"
    modify_pin65 = "- {{ pin_subpackage('dpcpp_impl_win-64')"
    replace_pin65 = "- {{ pin"
    modify_pin66 = "- {{ pin_subpackage('mpich')"
    replace_pin66 = "- {{ pin"
    modify_pin67 = "- {{ pin_subpackage('importlib-metadata')"
    replace_pin67 = "- {{ pin"
    modify_pin68 = "- {{ pin_subpackage('libedit')"
    replace_pin68 = "- {{ pin"
    modify_pin69 = "- {{ pin_subpackage('geos')"
    replace_pin69 = "- {{ pin"
    modify_pin70 = "- {{ pin_subpackage('at-spi2-atk')"
    replace_pin70 = "- {{ pin"
    modify_pin71 = "- {{ pin_compatible('dbus')"
    replace_pin71 = "- {{ pin"
    modify_pin72 = '- {{ pin_subpackage("aws-c-common")'
    replace_pin72 = "- {{ pin"
    modify_pin73 = "- {{ pin_subpackage('hdf5')"
    replace_pin73 = "- {{ pin"
    modify_pin74 = "- {{ pin_subpackage('libgdal')"
    replace_pin74 = "- {{ pin"
    modify_pin75 = "- {{ pin_subpackage('kealib')"
    replace_pin75 = "- {{ pin"
    modify_pin76 = "- {{ pin_subpackage('libiconv')"
    replace_pin76 = "- {{ pin"
    modify_pin77 = '- {{ pin_subpackage("aws-sdk-cpp")'
    replace_pin77 = "- {{ pin"
    modify_pin78 = "- {{ pin_subpackage('libpq')"
    replace_pin78 = "- {{ pin"    
    modify_pin79 = "- {{ pin_subpackage('jpeg')"
    replace_pin79 = "- {{ pin"
    modify_pin80 = '- {{ pin_subpackage("aws-c-event-stream")'
    replace_pin80 = "- {{ pin"
    modify_pin81 = "- {{ pin_subpackage('tk')"
    replace_pin81 = "- {{ pin"
    modify_pin82 = "- {{ pin_subpackage('libnetcdf')"
    replace_pin82 = "- {{ pin"
    modify_pin83 = '- {{ pin_subpackage("mpc")'
    replace_pin83 = "- {{ pin"
    modify_pin84 = "- {{ pin_subpackage('libssh2')"
    replace_pin84 = "- {{ pin"
    modify_pin85 = "- {{ pin_subpackage('prompt-toolkit')"
    replace_pin85 = "- {{ pin"
    modify_pin86 = "- {{ pin_subpackage('harfbuzz')"
    replace_pin86 = "- {{ pin"
    modify_pin87 = '- {{ '
    replace_pin87 = "- {{ pin"
    modify_pin88 = '- {{ '
    replace_pin88 = "- {{ pin"
    modify_pin89 = '- {{ '
    replace_pin89 = "- {{ pin"
    modify_pin90 = '- {{ '
    replace_pin90 = "- {{ pin"

    

    modify_os = "os.environ.get('PY_INTERP_DEBUG', '')"
    replace_os = "os"

    modify_comment = "# string: py{{ ''.join(python.split('.')[0:2]) }}h{{ PKG_HASH }}_{{ PKG_BUILDNUM }}{{ debug }}"
    replace_comment = ""

    #replace template conditionals if elif else endif if they are commented out
    modify_conditional = "# {% if false %}"
    replace_conditional = ""

    # set the location of the temporary files
    child_dir = "Temp"
    top_location = current_directory()
    file_location = "{0}/{1}/".format(top_location,child_dir)
    temp_file = "{0}meta.yaml".format(file_location)
    new_file = "{0}{1}-meta.yaml".format(file_location,recipe_name)

    # check first if the temporary file exists
    temp_file_status = Path(temp_file).exists()

    # display information
    #print("---------------------")
    #print("Modify Temporary File")
    #print("File_location: {0}".format(file_location))
    #print("Temp_file: {0}".format(temp_file))
    #print("New_file: {0}".format(new_file))
    #print("---------------------")
    
    # if the temporary file exists then update it
    if(temp_file_status is True):
        print("Temporary file: {0}\nModify_compiler: {1}\nReplace_compiler: {2}".format(temp_file,modify_compiler,replace_compiler))
            # replace the lines in the meta.yaml that are used for the jinja2 template
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_compiler, replace_compiler))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_compiler2, replace_compiler2))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_compiler3, replace_compiler3))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_compiler4, replace_compiler4))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_compiler5, replace_compiler5))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_compiler6, replace_compiler6))

        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_runtime, replace_runtime))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_runtime2, replace_runtime2))

        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_cdt, replace_cdt))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_cdt2, replace_cdt2))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_cdt3, replace_cdt3))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_cdt4, replace_cdt4))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_cdt5, replace_cdt5))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_cdt6, replace_cdt6))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_cdt7, replace_cdt7))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_cdt8, replace_cdt8))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_cdt9, replace_cdt9))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_cdt10, replace_cdt10))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_cdt11, replace_cdt11))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_cdt12, replace_cdt12))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_cdt13, replace_cdt13))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_cdt14, replace_cdt14))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_cdt15, replace_cdt15))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_cdt16, replace_cdt16))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_cdt17, replace_cdt17))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_cdt18, replace_cdt18))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_cdt19, replace_cdt19))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_cdt20, replace_cdt20))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_cdt21, replace_cdt21))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_cdt22, replace_cdt22))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_cdt23, replace_cdt23))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_cdt24, replace_cdt24))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_cdt25, replace_cdt25))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_cdt26, replace_cdt26))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_cdt27, replace_cdt27))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_cdt28, replace_cdt28))

        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_min_pin, replace_min_pin))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_min_pin2, replace_min_pin2))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_min_pin3, replace_min_pin3))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_min_pin4, replace_min_pin4))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_min_pin5, replace_min_pin5))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_min_pin6, replace_min_pin6))

        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_max_pin, replace_max_pin))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_max_pin2, replace_max_pin2))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_max_pin3, replace_max_pin3))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_max_pin4, replace_max_pin4))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_max_pin5, replace_max_pin5))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_max_pin6, replace_max_pin6))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_max_pin7, replace_max_pin7))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_max_pin8, replace_max_pin8))

        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_exact, replace_exact))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_target_platform, replace_target_platform))

        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_pin, replace_pin))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_pin2, replace_pin2))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_pin3, replace_pin3))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_pin4, replace_pin4))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_pin5, replace_pin5))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_pin6, replace_pin6))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_pin7, replace_pin7))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_pin8, replace_pin8))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_pin9, replace_pin9))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_pin10, replace_pin10))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_pin11, replace_pin11))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_pin12, replace_pin12))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_pin13, replace_pin13))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_pin14, replace_pin14))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_pin15, replace_pin15))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_pin16, replace_pin16))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_pin17, replace_pin17))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_pin18, replace_pin18))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_pin19, replace_pin19))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_pin20, replace_pin20))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_pin21, replace_pin21))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_pin22, replace_pin22))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_pin23, replace_pin23))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_pin24, replace_pin24))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_pin25, replace_pin25))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_pin26, replace_pin26))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_pin27, replace_pin27))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_pin28, replace_pin28))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_pin29, replace_pin29))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_pin30, replace_pin30))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_pin31, replace_pin31))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_pin32, replace_pin32))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_pin33, replace_pin33))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_pin34, replace_pin34))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_pin35, replace_pin35))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_pin36, replace_pin36))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_pin37, replace_pin37))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_pin38, replace_pin38))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_pin39, replace_pin39))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_pin40, replace_pin40))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_pin41, replace_pin41))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_pin42, replace_pin42))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_pin43, replace_pin43))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_pin44, replace_pin44))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_pin45, replace_pin45))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_pin46, replace_pin46))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_pin47, replace_pin47))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_pin48, replace_pin48))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_pin49, replace_pin49))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_pin50, replace_pin50))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_pin51, replace_pin51))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_pin52, replace_pin52))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_pin53, replace_pin53))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_pin54, replace_pin54))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_pin55, replace_pin55))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_pin56, replace_pin56))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_pin57, replace_pin57))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_pin58, replace_pin58))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_pin59, replace_pin59))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_pin60, replace_pin60))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_pin61, replace_pin61))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_pin62, replace_pin62))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_pin63, replace_pin63))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_pin64, replace_pin64))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_pin65, replace_pin65))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_pin66, replace_pin66))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_pin67, replace_pin67))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_pin68, replace_pin68))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_pin69, replace_pin69))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_pin70, replace_pin70))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_pin71, replace_pin71))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_pin72, replace_pin72))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_pin73, replace_pin73))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_pin74, replace_pin74))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_pin75, replace_pin75))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_pin76, replace_pin76))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_pin77, replace_pin77))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_pin78, replace_pin78))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_pin79, replace_pin79))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_pin80, replace_pin80))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_pin81, replace_pin81))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_pin82, replace_pin82))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_pin83, replace_pin83))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_pin84, replace_pin84))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_pin85, replace_pin85))
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_pin86, replace_pin86))

        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_os, replace_os))

        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_comment, replace_comment))

        # replace template conditionals if they are commented out
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_conditional, replace_conditional))


        # render the temporary file
        render_meta_file(recipe_name)

        #replace_template(temp_file, line_to_modify, line_to_replace)
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(line_to_modify, line_to_replace))
        #replace_template(temp_file, modify_script2, replace_script2)
#        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
#            sys.stdout.write(line.replace(modify_script2, replace_script2))
        # replace the script section
#        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
#            sys.stdout.write(line.replace(modify_script,replace_script))

        # replace the name section
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_name,replace_name))

        # replace the name section
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_version,replace_version))
        
        # replace tabs by spaces
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace('\t','    '))
        
        # replace tabs by spaces
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_template,replace_template))

        # replace empty urls
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_url,replace_url))

        # replace fn template
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_fn,replace_fn))
        
        # replace fn template
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_sha256,replace_sha256))
        
        # replace fn template
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_template2,replace_template2))


        # replace fn template
        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
            sys.stdout.write(line.replace(modify_number,replace_number))

        # replace fn template
#        for i, line in enumerate(fileinput.input(temp_file, inplace=1)):
            # replace the jinja2 template sections
#            sys.stdout.write(line.replace(modify_number2,replace_number2))


        # change the name of the temporary file
        # https://docs.python.org/3/library/os.html#os.rename
        os.rename(temp_file, new_file)

    pass

# delete temporary file
def delete_temporary_file():
    pass

# Gathere the test information from the meta.yaml file
def find_meta_info(recipe):

    # Declare variables
    current_path = current_directory()
    
    # set the path of the meta_file_path on the temporary folder
    meta_file_path = "{0}/Temp/{1}-meta.yaml".format(current_path,recipe)


    # generate the temporary file
    generate_temporary_file(recipe)
    modify_temporary_file(recipe)
    #render_meta_file(recipe)

    # verify if the temporary file exists
    meta_file_path_status = Path(meta_file_path).exists()

    # if the temporary file exists then modify 
    if(meta_file_path_status is True):
        # try to open the file
        with open(meta_file_path, "r") as stream:
            try:
                result = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                result = exc
                print(exc)

    # ---------------------------

    # loop to find the recipes in aggregate
#    for recipe in dir_list:

        # set the path of the yaml file
#        current_path = current_directory()
#        meta_file_path = "{0}/aggregate/{1}/recipe/meta.yaml".format(current_path,recipe)

        # open the meta.yaml file
#        print("Open the {0} meta.yaml file".format(recipe))
#        print("{0} \n".format(meta_file_path))
        return result

def find_test_data(meta_info):

        # declare variables
        contains_import_test = False
        contains_commands_test = False
        contains_requires_test = False

        # verify if the meta_info has data before
        if(meta_info is not None):
            print("Meta_info:")
            print(meta_info)
            print("Meta_info.keys():")
            print(meta_info.keys())
            test_data = meta_info.get("test")
            print("test data:")
            print(test_data)
            # check if test_data is available
            if (test_data is None):
                test_requires = None
                test_imports = None
                test_commands = None
            else:
                # if the test data is available then set the test data
                test_requires = test_data.get("requires")
                test_imports = test_data.get("imports")
                test_commands = test_data.get("commands")
            # check if  test_require is available
            if (test_requires is None):
                test_requires_size = 0
            else:
                test_requires_size = len(test_requires)
            print("requires:")
            print(test_requires)
            print("requires size: {0}".format(test_requires_size))
            #test_imports = test_data.get("imports")
            # check if test_import is available
            if (test_imports is None):
                test_imports_size = 0
            else:
                test_imports_size = len(test_imports)
            print("import:")
            print(test_imports)
            print("import size: {0}".format(test_imports_size))
            #test_commands = test_data.get("commands")
            # check if test_commands are available
            if (test_commands is None):
                test_commands_size = 0
            else:
                test_commands_size = len(test_commands)
            print("commands:")
            print(test_commands)
            print("commands size: {0}".format(test_commands_size))

            # determine if the meta.yaml file has tests
            # verify if the import test is present
            if(test_imports_size > 0):
                contains_import_test = True

            # verify if the commands are included in the test section
            if(test_commands_size > 0):
                contains_commands_test = True


    
            return test_data, contains_import_test, contains_commands_test

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
    file_name_none = "No_file_{0}_{1}_{2}.md".format(month_name, day_number, year_number) 
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
    missing_file_result, missing_file_list = missing_file(dir_list)
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

    # report file with no test files
    
    # set the report information
    body = "## Report"+space
    # loop to add elements to file
    for missing_file_package in missing_file_list:

        # find the document existing
        body = body + "- `{0}` \n".format(missing_file_package[0])

    reportTotal = header+body

    with open(file_location + file_name_none, 'w') as f:
        f.write(reportTotal)

    # --

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

    # report package with two test files

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

    # report package with three test files

    # set the  report information
    body = "## Report"+space

    # loop to add elements to file
    for three_file_package in three_file_list:
    
        body = body + "-`{0}` \n".format(three_file_package[0])
        body = body + "\t (test_run.sh, test_run.py, test_run.bat) \n"

    reportTotal = header + body

    with open(file_location + file_name_three,'w') as f:
        f.write(reportTotal)
    
    # gather meta.yaml file data
    #find_meta_info(dir_list)

    # ----------------- Gather Test Information ------------------
    
    #loop to gather the test information
    for recipe in dir_list:
        recipe_result = find_meta_info(recipe)
        # verify if there is information for the meta file
        if(recipe_result is not None):
            test_data, import_test, commands_test = find_test_data(recipe_result)
            print(recipe)
            print("Import Test: {0} | Commands in Test: {1}".format(import_test, commands_test))
            print(test_data)
            print("")

    # ------------------------------------------------------------

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

        # ------------------------------------

        # generate temporary files that will be used to gather meta.yaml info
        #generate_temporary_file("certipy-feedstock") 

        # modify the temporary files
        #modify_temporary_file("certipy-feedstock")

        # get the list of meta.yaml information from aggregate
        recipe_result = find_meta_info(recipes)
        #print(recipe_result.keys())
        #test_data = recipe_result.get('test')
        #print(test_data)
        #test_commands = test_data.get('commands')
        #test_commands_size = len(test_commands)
        #print(test_commands)
        #print(test_commands_size)
        test_data, import_test, commands_test = find_test_data(recipe_result)


if __name__ == '__main__':
    sys.exit(main())
