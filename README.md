# namelist-creater
Create e-mail and user name lists from firstname/lastname input. Can output raw lists or GoPhish CSV Output. Supports cli-supplied customized naming schemas. Attempts to handle non-ascii characters and double names with hyphen (e.g. John-John Smith-Roberts).
### Goals of this project
* Simplify tasks for Red Teamers after the reconnaissance phase
* Starting from a list of target names quickly create user name lists for password spraying and e-mail addresses for phishing campaigns
* Handle edge cases or malformed input gracefully (hopefully) with customization options
* Provide customizable schema handling
* Dust off my python skills :)

## Prerequisites
  ```sudo pip3 install unidecode```

## Usage
### Help
```python3 corgon.py -h
usage: corgon.py [-h] [-f {gophish_csv,emails,usernames}] [-d DELIMITER]
                 [-m MAILDOMAIN] [-s SCHEMA] [-a AD_DOMAIN] [--keepcase]
                 [--hyphenfn] [--hyphenln]
                 Infile Outfile

Turn a list of names into user names and e-mail addresses

positional arguments:
  Infile                Text File that contains names of people
  Outfile               Output file to write to

optional arguments:
  -h, --help            show this help message and exit
  -f {gophish_csv,emails,usernames}, --function {gophish_csv,emails,usernames}
                        Name List Delimiter (default is gophish_csv)
  -d DELIMITER, --delimiter DELIMITER
                        Name List Delimiter (default is whitespace(s))
  -m MAILDOMAIN, --maildomain MAILDOMAIN
                        Name of the e-mail Domain (default is @example.com)
  -s SCHEMA, --schema SCHEMA
                        Schema for username/mailname (default is
                        firstname.lastname for mail and only lastname for
                        user). Provide the order of first/last and delimiter
                        (if any). Examples: f1l->jsmith, l1f->sjohn,
                        f1.l->j.smith, l->smith
  -a AD_DOMAIN, --ad_domain AD_DOMAIN
                        Active Directory Domain. Is prepended to usernames in
                        case of -f usernames.
  --keepcase            Keep Casing of letters in output for email addresses
                        and usernames (default is false)
  --hyphenfn            Keep Hyphens in first name (default is not set)
  --hyphenln            Keep Hyphens in last name (default is not set)

```

### Examples
Create GoPhish CSV output for email addresses @example.com. Firstname.Lastname schema (default): 
```
$ python3 corgon.py -f gophish_csv -d " " -m @example.com names.txt emails_out.csv
[+] Parsing input file
[+] Selected Gophish CSV output function
[+] Output written to emails_out.csv
$ cat emails_out.csv 
First Name,Last Name,Position,Email
John,Smith,,John.Smith@example.com
Jane,Smith,,Jane.Smith@example.com
Jöhn,Smüth,,Joehn.Smueth@example.com
```
Create list of user names (non-AD) with JSmith naming schema:
```
$ python3 corgon.py -f usernames -d " " -s f1l --keepcase names.txt usernames_out.txt
[+] Parsing input file
[+] Selected username output function
[+] Output written to usernames_out.txt
$ cat usernames_out.txt
JSmith
JSmith
JSmueth
```
Create list of AD user names (with domain) with jo.smi naming schenma:
```
$ python3 corgon.py -a EXAMPLE -f usernames -d " " -s f2l3 names.txt ad_users_out.txt 
[+] Parsing input file
[+] Selected username output function
[+] Output written to ad_users_out.txt
cat ad_users_out.txt 
EXAMPLE\josmi
EXAMPLE\jasmi
EXAMPLE\joesmue
```
Schema examples (based on John Smith):
```
-s f1l2 -> jsm
-s f1.l -> jsmith
-s f1_l -> jsmith
-s f1.l --keepcase -> JSmith
-s l1.f -> sjohn
-s l-f -> smith-john
```
