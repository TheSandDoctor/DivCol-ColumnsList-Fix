#!/usr/bin/env python3.6
import mwclient, configparser, mwparserfromhell, argparse,re, pathlib
from time import sleep
import json

def call_home(site):
    #page = site.Pages['User:' + config.get('enwiki','username') + "/status"]
    page = site.Pages['User:DeprecatedFixerBot/status2']
    text = page.text()
    data = json.loads(text)["run"]["div_col"]
    if data:
        return True
    return False

        #if "false" in text.lower():
#   return False
#return True
def allow_bots(text, user):
    user = user.lower().strip()
    text = mwparserfromhell.parse(text)
    for tl in text.filter_templates():
        if tl.name in ('bots', 'nobots'):
            break
    else:
        return True
    for param in tl.params:
        bots = [x.lower().strip() for x in param.value.split(",")]
        if param.name == 'allow':
            if ''.join(bots) == 'none': return False
            for bot in bots:
                if bot in (user, 'all'):
                    return True
        elif param.name == 'deny':
            if ''.join(bots) == 'none': return True
            for bot in bots:
                if bot in (user, 'all'):
                    return False
    return True
def save_edit(page, utils, text):
    config = utils[0]

    site = utils[1]
    dry_run = utils[2]
    original_text = text
    if not dry_run:
        if not allow_bots(original_text, config.get('enwikidep','username')):
            print("Page editing blocked as template preventing edit is present.")
            return
    #print("{}".format(dry_run))
    code = mwparserfromhell.parse(text)
    for template in code.filter_templates():
        if template.name.matches("nobots") or template.name.matches("Wikipedia:Exclusion compliant"):
            if template.has("allow"):
                if "DeprecatedFixerBot" in template.get("allow").value:
                    break # can edit
            print("\n\nPage editing blocked as template preventing edit is present.\n\n")
            return
    if not call_home(site):#config):
        raise ValueError("Kill switch on-wiki is false. Terminating program.")
    time = 0
    edit_summary = """Removed deprecated parameter(s) from [[Template:Div col]]/[[Template:Columns-list]] using [[User:""" + config.get('enwikidep','username') + "| " + config.get('enwikidep','username') + """]]. Questions? See [[Template:Div col#Usage of "cols" parameter]] or [[User talk:TheSandDoctor|msg TSD!]] (please mention that this is task #2!))"""
    while True:
         #text = page.edit()
        if time == 1:
            text = site.Pages[page.page_title].text()
        try:
            content_changed, text = process_page(original_text,dry_run)
        except ValueError as e:
            """
            To get here, there must have been an issue figuring out the
            contents for the parameter colwidth.

            At this point, it is safest just to print to console,
            record the error page contents to a file in ./errors and append
            to a list of page titles that has had
            errors (error_list.txt)/create a wikified version of error_list.txt
            and return out of this method.
            """
            print(e)
            pathlib.Path('./errors').mkdir(parents=False, exist_ok=True)
            title = get_valid_filename(page.page_title)
            text_file = open("./errors/err " + title + ".txt", "w")
            text_file.write("Error present: " +  str(e) + "\n\n\n\n\n" + text)
            text_file.close()
            text_file = open("./errors/error_list.txt", "a+")
            text_file.write(page.page_title + "\n")
            text_file.close()
            text_file = open("./errors/wikified_error_list.txt", "a+")
            text_file.write("#[[" + page.page_title + "]]" + "\n")
            text_file.close()
            return
        try:
            if dry_run:
                print("Dry run")
                #Write out the initial input
                title = get_valid_filename(page.page_title)
                text_file = open("./tests/in " + title + ".txt", "w")
                text_file.write(original_text)
                text_file.close()
                #Write out the output
                if content_changed:
                    title = get_valid_filename(page.page_title)
                    text_file = open("./tests/out " + title + ".txt", "w")
                    text_file.write(text)
                    text_file.close()
                else:
                    print("Content not changed, don't print output")
                break
            else:
            #    print("Would have saved here")
            #    break
                #TODO: Enable
                page.save(text, summary=edit_summary, bot=True, minor=True)
                print("Saved page")
        except [[EditError]]:
            print("Error")
            time = 1
            sleep(5)   # sleep for 5 seconds before trying again
            continue
        except [[ProtectedPageError]]:
            print('Could not edit ' + page.page_title + ' due to protection')
        break
def get_valid_filename(s):
    """
    Turns a regular string into a valid (sanatized) string that is safe for use
    as a file name.
    Method courtesy of cowlinator on StackOverflow
    (https://stackoverflow.com/questions/295135/turn-a-string-into-a-valid-filename)
    @param s String to convert to be file safe
    @return File safe string
    """
    assert(s is not "" or s is not None)
    s = str(s).strip().replace(' ', '_')
    return re.sub(r'(?u)[^-\w.]', '', s)

def process_page(text,dry_run):
    wikicode = mwparserfromhell.parse(text)
    templates = wikicode.filter_templates()
    content_changed = False


    code = mwparserfromhell.parse(text)
    for template in code.filter_templates():
    #    template.name = template.name.lower()
        if (template.name.matches("columns-list") or template.name.matches("cmn")
        or template.name.matches("col list") or template.name.matches("col-list")
        or template.name.matches("collist") or template.name.matches("column list")
        or template.name.matches("columns list") or template.name.matches("columnslist")
        or template.name.matches("list-columns") or template.name.matches("listcolumns")):
            try:
                content_changed = do_cleanup_columns_list(template)
                print("done columns-list")
            except ValueError:
                raise





        if (template.name.matches("div col")):
            try:
                content_changed = do_cleanup_div_col(template)
            except ValueError:
                raise

        elif (template.name.matches("colbegin") or template.name.matches("cols")
        or template.name.matches("div 2col") or template.name.matches("div col begin")
        or template.name.matches("div col start") or template.name.matches("div-col")
        or template.name.matches("divbegin") or template.name.matches("divcol")
        or template.name.matches("divided column") or template.name.matches("palmares start")):
            #check for alias, if found, replace alias with proper template name and run cleanup
            print("Alternate template version (redirect to {{div col}})")
            template.name = "div col"
            try:
                content_changed = do_cleanup_div_col(template)
                print("done div col")
            except ValueError:
                raise
            #template.name.matches("col div end") doesn't need to be included,
            #as no need to change if present
        if (template.name.matches("colend")
        or template.name.matches("div col end") or template.name.matches("div end")
        or template.name.matches("div-col-end") or template.name.matches("divcol-end")
        or template.name.matches("divcolend") or template.name.matches("divend")
        or template.name.matches("end div col") or template.name.matches("enddivcol")
        or template.name.matches("palmares end")):
            #check for alias, if found, replace alias with proper template name
            print("Matched colend")
            template.name = "div col end"
    return [content_changed, str(code)] # get back text to save
def get_em_sizes(template, param):
    #param = str(param)
    #print("Value enter: " + str(template.get(param).value))
    is_not_digit = re.match(r'([0-9]+)em?',str(template.get(param).value))
    if is_not_digit:
        #template.get(param).value = is_not_digit.group(1)
        #if it already has "em", it will catch this regex and return the number bit
        #the raising of a ValueError down below is a catch-all (raises up to save_edit())
        print("Wasn't digit")
        return is_not_digit.group(1)
    try:
        if int(str(template.get(param).value)) < 2:
            print("FALSEEEEEEEE!")
            return False
        elif int(str(template.get(param).value)) == 2:
        #    print("value 2 or less, em 30")
            return 30
        elif int(str(template.get(param).value)) == 3:
        #    print("value 3, em 22")
            return 22
        elif int(str(template.get(param).value)) == 4:
    #        print("value 4, em 18")
            return 18
        elif int(str(template.get(param).value)) == 5:
    #        print("value 5, em 15")
            return 15
        elif int(str(template.get(param).value)) == 6:
        #    print("value 6, em 13")
            return 13
        elif int(str(template.get(param).value)) > 6:
        #    print("value greater 6, em 10")
            return 10
    except ValueError:
        raise

def do_cleanup_div_col(template):
    try:
        if template.has("cols"):
            size = get_em_sizes(template, "cols")
            template.remove("cols")
            if size:
                template.add("colwidth",str(size) + "em")
            return True
        if template.has("1") and template.has("2"):
            #TODO: remove 1, use 2
            template.remove("1",False)
            size = get_em_sizes(template, "2")
            template.remove("2",False)
            if size:
                template.add("colwidth",str(size) + "em")
            return True
        elif template.has("1"):
            #TODO: use 1, remove
            size = get_em_sizes(template, "1")
            template.remove("1")
            if size:
                template.add("colwidth",str(size) + "em")
            return True
        elif template.has("2"):
            size = get_em_sizes(template, "2")
            template.remove("2")
            if size:
                template.add("colwidth",str(size) + "em")
            return True
    except ValueError:
        raise

def do_cleanup_columns_list(template):
    try:
        if template.has("1"):
            size = get_em_sizes(template, "1")
            """
            Replace first param, since template.add won't work here as it would be added at end,
            which would not work or meet conventions. Due to this, best to just replace the first
            parameter as we have verified above that it is an unnamed parameter.
            """
            if size:
                template.params[0] = "colwidth=" + str(size) + "em"
            else:
                template.remove("1",False)  # remove since it is 1 (or less) and therefore redundant
            #template.replace("1","colwidth",str(size) + "em")
            #template.add("colwidth",str(size) + "em")
            return True
    except ValueError:
        raise

def single_run(title, utils, site):
    if title is None or title is "":
        raise ValueError("Category name cannot be empty!")
    if utils is None:
        raise ValueError("Utils cannot be empty!")
    if site is None:
        raise ValueError("Site cannot be empty!")
    print(title)
    page = site.Pages[title]#'3 (Bo Bice album)']
    text = page.text()

    try:
        #utils = [config,site,dry_run]
        save_edit(page, utils, text)#config, api, site, text, dry_run)#, config)
    except ValueError:# as err:
        raise
#print(err)
def category_run(cat_name, utils, site, offset,limited_run,pages_to_run):
    if cat_name is None or cat_name is "":
        raise ValueError("Category name cannot be empty!")
    if utils is None:
        raise ValueError("Utils cannot be empty!")
    if site is None:
        raise ValueError("Site cannot be empty!")
    if offset is None:
        raise ValueError("Offset cannot be empty!")
    if limited_run is None:
        raise ValueError("limited_run cannot be empty!")
    if pages_to_run is None:
        raise ValueError("""Seriously? How are we supposed to run pages in a
        limited test if none are specified?""")
    counter = 0
    for page in site.Categories[cat_name]:
        if offset > 0:
            offset -= 1
            print("Skipped due to offset config")
            continue
        print("Working with: " + page.name + " " + str(counter))
        if limited_run:
            if counter < pages_to_run:
                counter += 1
                text = page.text()
                try:
                    save_edit(page, utils, text)#config, api, site, text, dry_run)#, config)
                except ValueError:# as err:
                    raise
        #print(err)
            else:
                return  # run out of pages in limited run
def main():
    dry_run = False
    pages_to_run = 10
    offset = 0
    category = "Pages using Columns-list with deprecated parameters"#"Pages using div col with deprecated parameters"
    limited_run = True

    parser = argparse.ArgumentParser(prog='DeprecatedFixer Div col deprecation fixer', description='''Reads {{div col}} templates
    located inside the category "Pages using div col with deprecated parameters" (https://en.wikipedia.org/wiki/Category:Pages_using_div_col_with_deprecated_parameters).
    If it has unnamed 1st and/or 2nd parameter(s) or uses the parameter |cols (all deprecated). If the 1st unnamed parameter is found, it removes the parameter.
    If the 2nd unnamed parameter is found, then it removes the template and adds colwidth with the value of the 2nd unnamed parameter (plus "em").''')
    parser.add_argument("-dr", "--dryrun", help="perform a dry run (don't actually edit)",
                    action="store_true")
    #parser.add_argument("-arch","--archive", help="actively archive Tweet links (even if still live links)",
    #                action="store_true")
    args = parser.parse_args()
    if args.dryrun:
        dry_run = True
        print("Dry run")

    site = mwclient.Site(('https','en.wikipedia.org'), '/w/')
    if dry_run:
        pathlib.Path('./tests').mkdir(parents=False, exist_ok=True)
    config = configparser.RawConfigParser()
    config.read('credentials.txt')
    try:
        site.login(config.get('enwikidep','username'), config.get('enwikidep', 'password'))
    except errors.LoginError as e:
        #print(e[1]['reason'])
        print(e)
        raise ValueError("Login failed.")

    utils = [config,site,dry_run]
    try:
        #single_run('User:DeprecatedFixerBot/sandbox', utils, site)
    #User:TweetCiteBot/sandbox
        category_run(category, utils, site, offset,limited_run,pages_to_run)
        #category_run("Pages using div col with deprecated parameters", utils, site, offset,limited_run,pages_to_run)
    #    category_run("Pages using Columns-list with deprecated parameters", utils, site, offset,limited_run,pages_to_run)
    except ValueError as e:
        print("\n\n" + str(e))
    #config.read('credentials.txt')
    #TODO: site.login(config.get('enwiki','username'), config.get('enwiki', 'password'))

if __name__ == "__main__":
    main()
