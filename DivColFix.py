#!/usr/bin/env python3.6
import mwclient, configparser, mwparserfromhell, argparse
from time import sleep

def getopts(argv):
    opts = {}  # Empty dictionary to store key-value pairs.
    while argv:  # While there are arguments left to parse...
        if argv[0][0] == '-':  # Found a "-name value" pair.
            opts[argv[0]] = argv[1]  # Add key and value to the dictionary.
        argv = argv[1:]  # Reduce the argument list by copying it starting from index 1.
    return opts
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
         #text = text.replace('[[Category:Apples]]', '[[Category:Pears]]')
        if time == 1:
        #     page = site.Pages[page.page_title]
            text = site.Pages[page.page_title].text()
        #text = remove_param(original_text,dry_run)
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
#    print("In remove {}".format(dry_run))
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
#    print(code.get_sections())
    #text_file = open("sec.txt",'w')
    #text_file.write(str(code.get_sections()))
    #text_file.close()
    #for li in code.get_sections():
    #    print(li)
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
                #template.replace(str(template.get("1")),"colwidth",str(template.get("1").value) + "em")
                content_changed = True
            if template.has("2"):
                print("Has hidden param 2")
                col = template.get("2").value
                template.remove("2",False)
                template.add("colwidth",str(col))
            else:
                pass
            #    print(template.params[0].value)
            #    params_0 = template.params[0].value
            #    print("Val: " + str(params_0))
                #TODO: Doesn't work
                #template.remove(str(template.params[0].value))
                #template.remove(params_0)
            #    print("Val2d: " + str(params_0))
            #    template.add("colwidth", str(params_0) + "em")
            #    content_changed = True
            #print(template.params[0])

            #if template.has("writing_credits"):
            #    template.remove("writing_credits",False)
            #    print("Removed writing_credits")
            #if template.has("lyrics_credits"):
            #    template.remove("lyrics_credits",False)
            #    print("Removed lyrics_credits")
            #if template.has("music_credits"):
            #    template.remove("music_credits",False)
            #    print("Removed music_credits")
    return [content_changed, str(code)] # get back text to save
def main():

    #dry_run = False
    parser = argparse.ArgumentParser(prog='TweetCiteBot Tweet URL conversion', description='''Reads {{cite web}} templates
    on articles looking for url parameters containing Tweet URLs. If found, convert template to {{cite tweet}} and retrieve
    relevant information (if possible). If the Tweet is a dead link, attempt recovery with the Wayback archive and tag accordingly
    on-wiki. This task was approved by the English Wikipedia Bot Approvals Group at 17:59, 2 December 2017 (UTC) by BAG admin
    User:cyberpower678''')
    parser.add_argument("-dr", "--dryrun", help="perform a dry run (don't actually edit)",
                    action="store_true")
    parser.add_argument("-arch","--archive", help="actively archive Tweet links (even if still live links)",
                    action="store_true")
    args = parser.parse_args()
    if args.dryrun:
        dry_run = True
        print("Dry run")
    if args.archive:
        print("Archive allow")
        archive_urls = True

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
