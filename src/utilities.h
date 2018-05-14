#include <pybind11/pybind11.h>
#include <pybind11/embed.h>
#include <iostream>

bool call_home(pybind11::object site,std::string user_name);
void print_dict(pybind11::dict dict);
bool equal_case_insensitive(const std::string& s1, const std::string& s2);
#include <sys/stat.h>
namespace Helpers {
    pybind11::str get_valid_filename(std::string s) {
        pybind11::object re = pybind11::module::import("re");
        pybind11::object s1 = pybind11::str(s).attr("strip")().attr("replace")(' ','_');
        return re.attr("sub")("r'(?u)[^-\w.]'","",pybind11::str(s1));
    }
    bool is_invalid_literal(std::string error_msg)
    {
        if(error_msg.find("invalid literal for") != std::string::npos)
        {
           // pybind11::print("invalid literal error, skipping");
            return true;
        }
        return false;
    }
}
