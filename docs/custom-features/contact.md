# Contact

The Contact feature facilitates the management and display of contact information across the site. It offers flexibility in defining contact details for various pages and allows for customization of the Contact CTA block within the site-wide footer.

## Contact Model

The `tbx.people.Contact` model represents contact information, including details such as name, role, image, and call-to-action (CTA). It provides the following fields:

1. `title`: A descriptive title for the contact block, typically used as a heading.
2. `text`: Additional text to accompany the contact information, providing further context.
3. `cta`: Call-to-action block, allowing customization of a button link and text.
4. `name`: The name of the contact person or entity.
5. `role`: The role or position of the contact person.
6. `image`: An image associated with the contact.
7. `default_contact`: Flag to designate this contact as the default for the site.

The `Contact` model also includes functionality to:

- ensure only one default contact exists at a time;
- ensure that fields 1 to 6 above are filled out when creating or updating a contact. If any of these fields are missing, a validation error will be raised, prompting the user to provide the necessary information.

## ContactMixin

The `tbx.people.ContactMixin` provides a mechanism for associating a specific contact with a page. It offers the following functionality:

- `contact` field: Adds a ForeignKey field to associate a specific contact with a page.
- `footer_contact`: A cached property that determines the appropriate contact to display in the footer of a page. It first checks if the page has a specific contact assigned. If not, it traverses the page's ancestors to find the most relevant contact, eventually falling back to the default contact if none is specified.

???+ tip "Default Contact"

    It is good to ensure that there is always a default contact, as this is what will be used in the footer across the whole site, unless content editors specify their own contacts.

---

???+ note

    Please ensure that the Editors' guide is updated accordingly whenever any changes are made to this feature. A private link, for Torchbox employees only, can be found at https://intranet.torchbox.com/torchbox-com-project-docs.
