# Email signatures

These signatures use the brand colours and your monogram. They are plain HTML tables with inline
styles, which is the only kind of HTML that mail apps reliably keep.

## Files

- `_template.html`: the signature with `[NAME]`, `[TITLE]` and `[EMAIL]` left in, for anyone you add later.
- One `.html` file per person, already filled in.

## Host the logo image first

Mail apps load the small logo from a web address, so the image has to be online before the signature
will show it. The file is `brand/assets/logos/mark-tile-160.png`.

- Upload it to your website so it is available at `<your website>/brand/mark-tile-160.png`. The
  signatures are already written to use that address when your config has a website.
- If your config has no website, the signatures contain `[LOGO_URL]` instead. Upload the image
  anywhere public (your website, a public file store, a CDN) and replace `[LOGO_URL]` in each file with its full address.

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
