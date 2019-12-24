# namelist-creater
Create e-mail and user name lists from firstname/lastname input. Can output raw lists or GoPhish CSV Output.

## Prerequisits
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
Create GoPhish CSV output for email addresses @example.com: 
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

