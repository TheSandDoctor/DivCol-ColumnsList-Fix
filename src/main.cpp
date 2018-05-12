#include <pybind11/pybind11.h>
#include "utilities.cpp"
#include <iostream>
#include <sstream>
#include <string>
int add(int i, int j) {
    return i + j;
}
using namespace std;
template <class T>
bool from_string(T &t,
                 const std::string &s,
                 std::ios_base & (*f)(std::ios_base&))
{
    std::istringstream iss(s);
    return !(iss>>f>>t).fail();
}
namespace py = pybind11;
py::list gen_cat(py::object site,py::str cat) {
    py::list list;
    for(auto item : site.attr("Categories").attr("__getitem__")(cat)) {
        list.append(item);
    }
    return list;
}
void save_edit(py::handle page, py::list utils, py::str text)
{
    auto config = utils[0];
    auto site = utils[1];
    //bool bDry_run = (bool)utils[2];
    string Dry_run = string(py::str(utils[2]));
    bool bDry_run;
    bool bContent_changed = false;
    from_string<bool>(bDry_run, Dry_run, std::boolalpha);
    py::str original_text = text;
    py::object divcol = pybind11::module::import("DivColFix");
    if(!bDry_run && !divcol.attr("allow_bots")(original_text,config.attr("get")("enwikidep","username")))
    {
        py::print("Page editing blocked as template preventing edit is present.");
        return;
    }
    py::object mwparser = pybind11::module::import("mwparserfromhell");
    py::object mwclient = pybind11::module::import("mwclient");
    py::str code = mwparser.attr("parse")(text);
   /* for(auto temp : code.attr("filter_templates")())
    {
        if(temp.attr("name").attr("matches")("nobots") ||
           temp.attr("name").attr("matches")("Wikipedia:Exclusion compliant"))
        {
           // if(temp.attr("has")("allow") && string("DeprecatedFixerBot").find(temp.attr("get")("allow").attr("value")))
            if(temp.attr("has")("allow") && string("DeprecatedFixerBot").find(py::str(temp.attr("get")("allow").attr("value"))))
                break;
            py::print("\n\nPage editing blocked as template preventing edit is present.\n\n");
            return;
        }
    }*/
    if(!call_home(site, "DeprecatedFixerBot"))
        throw new std::domain_error("Kill switch on-wiki is false. Terminating program.");
    int time = 0;
    string edit_summary = string("""Removed deprecated parameter(s) from [[Template:Div col]]/[[Template:Columns-list]] using [[User:""") + string(py::str(config.attr("get")("enwikidep","username"))) + string("| ") + string(py::str(config.attr("get")("enwikidep","username"))) + string("""]]. Questions? See [[Template:Div col#Usage of \"cols\" parameter]] or [[User talk:TheSandDoctor|msg TSD!]] (please mention that this is task #2!))""");
    py::object open = py::module::import("builtins").attr("open");
    while(1)
    {
        if(time == 1)
        {
            text = site.attr("Pages").attr("__getitem__")(page.attr("page_title")).attr("text")();
        }
        try
        {
            bContent_changed, text = divcol.attr("process_page")(original_text,bDry_run);
        }
        catch(std::domain_error e)
        {
            py::object pathlib = py::module::import("pathlib");
            py::print(e);
            pathlib.attr("Path")("./errors").attr("mkdir")(false,"exist_ok=True");
            auto title = Helpers::get_valid_filename(py::str(page.attr("page_title")));
            auto text_file = open(string("./errors/err") + string(title) + string(".txt"),"w");
            text_file.attr("write")(string("Error present: ") +  string(e.what()) + string("\n\n\n\n\n") + string(text));
            text_file.attr("close")();
            text_file = open("./errors/error_list.txt", "a+");
            text_file.attr("write")(string(py::str(page.attr("page_title"))) + string("\n"));
            text_file.attr("close");
            text_file = open("./errors/wikified_error_list.txt", "a+");
            text_file.attr("write")(string("#[[") + string(py::str(page.attr("page_title"))) + string("]]") + string("\n"));
            text_file.attr("close")();
            return;
        }
        try {
            if(bDry_run) {
                py::print("Dry run");
                auto title = Helpers::get_valid_filename(string(py::str(page.attr("page_title"))));
                auto text_file = open(string("./tests/in ") + string(title) + string(".txt"),"w");
                text_file.attr("write")(text);
                text_file.attr("close")();
                if(bContent_changed)
                {
                    py::print("Content changed");
                    title = Helpers::get_valid_filename(string(py::str(page.attr("page_title"))));
                    text_file = open(string("./tests/out ") + string(title) + string(".txt"),"w");
                    text_file.attr("write")(text);
                    text_file.attr("close")();
                }
                else
                {
                    py::print("Content not changed, don't print output");
                }
                break;
            }
            else
            {
                page.attr("save")(text,edit_summary,true,true);
                py::print("Saved page");
            }
            // I would prefer the below design, but need to figure out how to implement as below code does not compile
        } /*catch (mwclient.attr("ProtectedPageError")()) {
            py::print(string("Could not edit ") + string(py::str(page.attr("page_title"))) + string(" due to protection"));
           } */catch(...){//mwclient.attr("EditError")()) {
            py::print("Error");
               if(time == 0)
                   time = 1;
               else
                   time = 2;
               if(time == 2)
                   break;   // clearly not working after second try, so best to just move on
            py::object sleep = py::module::import("time").attr("sleep");
            sleep(5);
            continue;
        }
        break;
    }
}
void process(py::object site, py::str cat_name, py::list utils, int offset, bool limited_run, int pages_to_run) {
    if(string(cat_name) == "" || cat_name == NULL || utils == NULL || site == NULL) {
        throw new std::domain_error("Inputs invalid");
    }
    int counter = 0;
    py::object divcol = pybind11::module::import("DivColFix");
    for(auto item : site.attr("Categories").attr("__getitem__")(cat_name))
    {
        if(offset > 0) {
            offset -= 1;
            cout << "Skipped due to offset config\n";
            continue;
        }
        cout << string("Working with: ") + string(py::str(item.attr("name"))) + string(" ") + to_string(counter);
        if(limited_run)
        {
            if(counter < pages_to_run)
            {
                counter += 1;
                py::str text = item.attr("text")();
                try{
                 //   divcol.attr("save_edit")(item,utils,text);
                    cout << "Saved\n";
                 //   py::object builtins = pybind11::module::import("utils_custom");
                    save_edit(item,utils,text);
                }catch(std::domain_error e) {
                    throw e;
                }
            } else { return; }
        }
    }
}
/**
 * @brief Checks if a given page name is in a python list object
 *
 * @param page_name Name of page to check
 * @param list Python list object to check
 * @return True if found, false otherwise
 */
bool pageInList(std::string page_name,py::list list) {
    // sortArray(py::str(list))
    for(auto item:list) {
        if(page_name.compare(py::str(item)) == 0){//if(page_name.find(py::str(item)) != string::npos) {
            //cout << string(py::str(item));
            return true;
        }
    }
    return false;
}



bool do_cleanup_columns_list(py::object temp)
{
    py::object utils = pybind11::module::import("utils_custom");
    py::object builtins = py::module::import("builtins");
    try{
        if(temp.attr("has")("1")) {
            py::object size = utils.attr("get_em_sizes")(temp,"1");
            if(builtins.attr("isinstance")(size,builtins.attr("int"))) {
                temp.attr("params").attr("__getitem")(0) = py::str(string("colwidth=") + string(py::str(size)) + string("em"));
            }
            if(size == Py_False) {
                temp.attr("remove")("1",false);
            }
            return true;
        }
    }catch(std::domain_error e){
        throw e;
    }
    return false;
}
py::list process_page(py::str text, bool dry_run)
{
    py::object mwparser = pybind11::module::import("mwparserfromhell");
    py::object wikicode = mwparser.attr("parse")(text);
    py::object templates = wikicode.attr("filter_templates")();
    bool bContent_changed = false;
    py::object code = mwparser.attr("parse")(text);
    for(auto temp:code.attr("filter_templates")())
    {
        if(equal_case_insensitive(py::str(temp.attr("name")),"columns-list") ||
           equal_case_insensitive(py::str(temp.attr("name")),"cmn") ||
        equal_case_insensitive(py::str(temp.attr("name")),"col list") ||
        equal_case_insensitive(py::str(temp.attr("name")),"col-list") ||
        equal_case_insensitive(py::str(temp.attr("name")),"collist") ||
        equal_case_insensitive(py::str(temp.attr("name")),"column list") ||
        equal_case_insensitive(py::str(temp.attr("name")),"columns list") ||
        equal_case_insensitive(py::str(temp.attr("name")),"columnslist") ||
        equal_case_insensitive(py::str(temp.attr("name")),"list-columns") ||
        equal_case_insensitive(py::str(temp.attr("name")),"listcolumns"))
        {
            try {
             //   bContent_changed = do_cleanup_columns_list(temp);
            } catch(std::domain_error e){
                throw e;
            }
        }
    }
    py::list e;
    return e;
}
PYBIND11_MODULE(divcolfixer, m) {
    m.def("call_home",&call_home);
    //process(py::object site, py::str cat_name, py::list utils, int offset, bool limited_run, int pages_to_run)
    m.def("process",&process);
}