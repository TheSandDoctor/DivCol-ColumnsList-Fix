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
            #pass
            if template.has("cols"):
                #cols = template.get("cols").value
                template.remove("cols")
                #template.add("colwidth", str(cols) + "em")
                content_changed = True
            elif template.has("1"):
                print("This exists! :D")
            #    col = template.get("1").value
                template.remove(template.get("1"),False)
            #    template.add("colwidth", str(col) + "em")
                content_changed = True
            if template.has("2"):
                print("Has hidden param 2")
                col = template.get("2").value
                template.remove("2",False)
                template.add("colwidth",str(col) + "em")
            else:
                pass

    return [content_changed, str(code)] # get back text to save
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
