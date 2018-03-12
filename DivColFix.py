#!/usr/bin/env python3.6
import mwclient, configparser, mwparserfromhell, argparse
from time import sleep

def call_home(site):#config):
    #page = site.Pages['User:' + config.get('enwiki','username') + "/status"]
    page = site.Pages['User:TweetCiteBot/status']
    text = page.text()
    if "false" in text.lower():
        return False
    return True
def save_edit(page, utils, text):
    config = utils[0]

    site = utils[1]
    dry_run = utils[2]
    original_text = text

    #if not allow_bots(original_text, config.get('enwiki','username')):
    #    print("Page editing blocked as template preventing edit is present.")
    #    return
    #print("{}".format(dry_run))
    code = mwparserfromhell.parse(text)
    for template in code.filter_templates():
        if template.name.matches("nobots") or template.name.matches("Wikipedia:Exclusion compliant"):
            if template.has("allow"):
                if "TweetCiteBot" in template.get("allow").value:
                    break # can edit
            print("\n\nPage editing blocked as template preventing edit is present.\n\n")
            return
    if not call_home(site):#config):
        raise ValueError("Kill switch on-wiki is false. Terminating program.")
    time = 0
    while True:
         #text = page.edit()
        if time == 1:
            text = site.Pages[page.page_title].text()
        content_changed, text = remove_param(original_text,dry_run)
        try:
            if dry_run:
                print("Dry run")
                #Write out the initial input
                text_file = open("Input03.txt", "w")
                text_file.write(original_text)
                text_file.close()
                #Write out the output
                if content_changed:
                    text_file = open("Output03.txt", "w")
                    text_file.write(text)
                    text_file.close()
                else:
                    print("Content not changed, don't print output")
                break
            else:
                print("Would have saved here")
                break
                #TODO: Enable
                #page.save(text, summary='Removed deprecated parameter(s) from [[Template:Track listing]]', bot=True, minor=True)
        except [[EditError]]:
            print("Error")
            time = 1
            sleep(5)   # sleep for 5 seconds before trying again
            continue
        except [[ProtectedPageError]]:
            print('Could not edit ' + page.page_title + ' due to protection')
        break

def remove_param(text,dry_run):
    wikicode = mwparserfromhell.parse(text)
    templates = wikicode.filter_templates()
    content_changed = False
    #TODO: Testing (dry run) only
    if dry_run:
        text_file = open("Input.txt","w")
        text_file.write(text)
        text_file.close()
    #TODO: End dry run only
    code = mwparserfromhell.parse(text)
    for template in code.filter_templates():#Tracklist, Track, Soundtrack, Tlist, Track list
        template.name = template.name.lower()
        #print(template.name)
        if (template.name.matches("div col")):
            content_changed = do_cleanup(template)
        elif (template.name.matches("colbegin") or template.name.matches("cols")
        or template.name.matches("div 2col") or template.name.matches("div col begin")
        or template.name.matches("div col start") or template.name.matches("div-col")
        or template.name.matches("divbegin") or template.name.matches("divcol")
        or template.name.matches("divided column") or template.name.matches("palmares start")):
            #check for alias, if found, replace alias with proper template name and run cleanup
            print("Alternate template version (redirect to {{div col}})")
            template.name = "div col"
            content_changed = do_cleanup(template)
            print("done")
            pass
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
    em = None
    if int(str(template.get(param).value)) <= 2:
    #    print("value 2 or less, em 30")
        return 30#em = 0
    elif int(str(template.get(param).value)) == 3:
    #    print("value 3, em 22")
        return 22#em = 22
    elif int(str(template.get(param).value)) == 4:
#        print("value 4, em 18")
        return 18#em = 18
    elif int(str(template.get(param).value)) == 5:
#        print("value 5, em 15")
        return 15#em = 15
    elif int(str(template.get(param).value)) == 6:
    #    print("value 6, em 13")
        return 13#em = 13
    elif int(str(template.get(param).value)) > 6:
    #    print("value greater 6, em 10")
        return 10#em = 10
    return em

def do_cleanup(template):
    if template.has("cols"):
        #cols = template.get("cols").value
        #size = template.get("cols").value
        size = get_em_sizes(template, "cols")
        template.remove("cols")
        template.add("colwidth",str(size) + "em")
    #    print("Cols")
        #template.add("colwidth", str(cols) + "em")
        return True
    if template.has("1") and template.has("2"):
        #TODO: remove 1, use 2
        template.remove("1",False)
        size = get_em_sizes(template, "2")
        template.remove("2",False)
        template.add("colwidth",str(size) + "em")
    #    print("1 and 2 " + str(size))
        return True
    #    pass
    elif template.has("1"):
        #TODO: use 1, remove
        size = get_em_sizes(template, "1")
        template.remove("1")
        template.add("colwidth",str(size) + "em")
    #    print("1")
        return True
    #    pass
    elif template.has("2"):
        #TODO: use 2
        size = get_em_sizes(template, "2")
        template.remove("2")
        template.add("colwidth",str(size) + "em")
    #    print("2")
        return True
def main():
    #dry_run = False
    parser = argparse.ArgumentParser(prog='TweetCiteBot Div col deprecation fixer', description='''Reads {{div col}} templates
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
#    if args.archive:
#        print("Archive allow")
#        archive_urls = True

    site = mwclient.Site(('https','en.wikipedia.org'), '/w/')
    config = configparser.RawConfigParser()
    #config.read('credentials.txt')
    #TODO: site.login(config.get('enwiki','username'), config.get('enwiki', 'password'))
    page = site.Pages['User:TweetCiteBot/sandbox']#'3 (Bo Bice album)']
    text = page.text()

    try:
        utils = [config,site,dry_run]
        save_edit(page, utils, text)#config, api, site, text, dry_run)#, config)
    except ValueError as err:
        print(err)
if __name__ == "__main__":
    main()
