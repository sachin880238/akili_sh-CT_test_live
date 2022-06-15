import os
import getpass

def assign_default_arrow_color(cr, registry):
    user_name=getpass.getuser()
    dir_path = '/home/'+user_name
    for root, _, files in os.walk(dir_path):
        for file in files:
            if file.endswith(".scss"):
                path = os.path.join(root, file)
                if file == 'primary_variables.scss' and ".local/share" not in path and 'website_custom_menu' in path:
                    with open(os.path.join(root, file), 'r') as file:
                        # read a list of lines into data
                        data = file.readlines()
                        data[5] = "$o-web-icon-arrow-color: " + '#F5F4F0' + ";\n"
                        with open(path, 'w') as file:
                            file.writelines(data)
                    break
