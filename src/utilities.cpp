#include "utilities.h"
void print_dict(pybind11::dict dict){
    for(auto item:dict){
        std::cout << "key=" << std::string(pybind11::str(item.first)) << ", "
        << "value="<< std::string(pybind11::str(item.second))<<std::endl;
    }
}
/**
 * @brief Check if the killswitch has been set to false or not.
 *
 * @param site mwclient site object
 * @param user_name User name to change the status page of (/status sub-page MUST exist to use this!)
 * @return True if it is okay to edit, false if the kill switch has been set to false
 */
bool call_home(pybind11::object site, std::string user_name){
    //py::print(py::str(site));
    pybind11::object page = site.attr("Pages").attr("__getitem__")("User:" + user_name + "/status2");
    pybind11::object json = pybind11::module::import("json");
    auto text = page.attr("text")();
    auto data = json.attr("loads")(text).attr("__getitem__")("run").attr("__getitem__")("div_col");
    if(pybind11::str(data).is(pybind11::str(Py_True))) {
        return true;
    }
    return false;
}

/**
 * @brief Compare two strings (case insensitive)
 *
 * @param s1 first string to compare
 * @param s2 second string to compare
 * @return True if equal, false otherwise
 */
bool equal_case_insensitive(const std::string& s1, const std::string& s2)
{
    return(0 == strcasecmp(s1.c_str(), s2.c_str()));
}
