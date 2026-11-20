# Email signatures

These signatures use the brand colours and your monogram. They are plain HTML tables with inline
styles, which is the only kind of HTML that mail apps reliably keep.

## Files

- `_template.html`: the signature with `[NAME]`, `[TITLE]` and `[EMAIL]` left in, for anyone you add later.
- One `.html` file per person, already filled in.

## Host the logo image first

Mail apps load the small logo from a web address, so the image has to be online before the signature
will show it. The file is `brand/assets/logos/mark-tile-160.png`. These signatures currently load it
from:

    https://brindlewick.example/brand/mark-tile-160.png

The address comes from `brand/assets/config.json`:

- If the config has a `logo_url`, the signatures use it as it is.
- Otherwise, if it has a `website`, they use `<website>/brand/mark-tile-160.png`. Use this only if you
  can put a file at exactly that address. Site builders such as Squarespace, Wix, Webflow and Framer
  usually cannot serve a file at a path you choose.
- With neither, the signatures contain `[LOGO_URL]`.

If you cannot use the website address, upload the PNG anywhere public (your site builder's image or
file upload, a public file store, a CDN), copy the address it gives you, set `logo_url` to it in
`config.json` and build the signatures again. You can also replace `[LOGO_URL]` by hand in each file.

Open the address in a private browser window to check that it loads without signing in.

## Install

Open the person's `.html` file in a browser, select everything on the page (Cmd+A or Ctrl+A) and
copy it. Then:

### Gmail

1. Settings, then See all settings, then General, then Signature.
2. Create a new signature, give it a name and paste into the box.
3. Choose it under "Signature defaults" for new emails and replies, then save.

### Apple Mail

1. Mail, then Settings, then Signatures.
2. Add a signature and paste into the preview box on the right.
3. Untick "Always match my default message font", or Mail will restyle the text.
4. If the paste loses its layout, quit Mail first, edit the saved signature file in
   `~/Library/Mail/V*/MailData/Signatures/` and replace its body with the contents of the `.html` file.

### Outlook

1. New Outlook and Outlook on the web: Settings, then Accounts, then Signatures. Create a signature and paste.
2. Classic Outlook: File, then Options, then Mail, then Signatures. Create a signature and paste.
3. Set it as the default for new messages and replies.

## Notes

- The brand font is listed first, followed by Arial. Most mail apps do not load custom fonts, so
  recipients will usually see Arial. The colours and layout still hold.
- Send yourself a test and look at it on a phone and in dark mode before rolling it out.
