# Crowdfunding Project

## Project Description

This crowdfunding platform is created to connect those who need to raise funds for personal issues or projects and those who are able to contribute. It is mainly targeted at those in need of financial assistance for medical expenses, education, emergencies, or community projects.

## Users

There are two main types of users on the platform:

- The **fundraisers**, who create campaigns to raise money for their causes or needs.
- The **donors**, who browse campaigns and contribute funds to support the causes they care about.

All users are required to create an account to participate in fundraising or donating activities. If they do not have an account, then they can view campaigns and events but not interact with them (i.e. cannot donate or raise). Accounts are created with basic information such as name, email, phone number, and password. An account needs to choose to be a donor or a fundraiser during the registration process, which cannot be changed later. In detail, the account creation process requires the following fields:

- Full legal name
- Email address (needs to be validated)
- Phone number (optional)
- Password (with strength requirements)
- User type (donor or fundraiser)

Fundraisers need to provide additional information during registration, including:

- A brief biography or description of themselves.

Donors can create donor groups to pool their resources and support campaigns together. Donor groups can have multiple members. Each donor group has one administrator who created the group, and can invite other donors to join, either via direct invitation or a group code. Donor groups can create campaigns dedicated to a fundraiser, or to a specific cause. When a member of a donor group donates to a campaign, the donation is tracked under the group. On the donor group page, the following info can be viewed:

- Group name and description
- List of members
- History of donations made by members on behalf of the group
- Total amount donated by the group

As a group admin, the user can also:

- Invite new members via direct invitation on the app, or by sharing a group code
- Remove members from the group
- View and manage the group's donation history
- Create campaigns on behalf of the group, dedicated to a fundraiser or cause

On any campaign page, if a donation is made by a donor group, the donation will be marked as from the group, and the group's name will be displayed among the list of donors. As a group member, the user can choose to donate individually or as part of the group with the selection of a checkbox during the donation process.

## Campaigns

Campaigns are the core feature of the platform. Campaigns can be created by the fundraisers, or by a donor group on behalf of a fundraiser. Each campaign page includes:

- A title and description of the cause or need. The description can include images and videos and support Markdown formatting.
- Relevant categories (e.g., medical, education, emergency, community), added during campaign creation.
- A fundraising goal amount.
- An end date for the campaign.
- The current amount raised so far and the number of donors.
- A list of recent donations, including donor names (if they choose to be recognized) and amounts.
- Posts of recent updates from the fundraiser about the campaign progress. These also support Markdown formatting.

Fundraisers can create and manage their campaigns through a dedicated dashboard, where they can:

- Create new campaigns by providing the necessary details.
- Edit existing campaigns to update information or extend the end date.
- View detailed statistics about donations, donor demographics, and campaign performance.
- Post updates to keep donors informed about the campaign's progress.

If a donor group created the campaign, the group admin can also manage the campaign similarly. The group can also create donation events, available to the public. An event includes a title, description, date, time, and location, and is linked to the campaign. Users can view events on the campaign page. They can add events to Google Calendar with a click of a button on the event details page.

Donors can search and filter campaigns based on name, category, end date, most recently created, and amount raised. Donors can also sort campaigns by amount raised, end date, and popularity (number of donors).

## Events

Events can be created to promote campaigns and encourage donations. Events are linked to specific campaigns and can include:

- Event title and description.
- Date, time, and location of the event.
- A link to the associated campaign.

## Donor-Fundraiser Pairing

The platform includes a special feature, whereby donors can be paired with fundraisers based on shared interests or causes. This pairing system helps build a community of support and encourages ongoing engagement between donors and fundraisers. Donors can opt-in to be paired with fundraisers, and the platform will suggest campaigns that align with their interests. Fundraisers can also reach out to their paired donors for additional support and updates.

## Security and Privacy

The platform prioritizes the security and privacy of its users. All personal and financial information is encrypted and securely stored. The platform complies with relevant data protection regulations to ensure user trust and safety. Passwords are hashed, and sensitive data is never stored in plain text.

In the demo, the data is stored in a local SQLite database, with encryption applied to sensitive fields.

## User Support

All user accounts can reach out to the website support team for assistance with any issues or questions. Support is available via email and live chat during business hours. A comprehensive FAQ section is also available to help users navigate the platform and resolve common issues.

## Third Party Integrations

The platform integrates with third-party services for payment processing, email notifications, and social media sharing. These integrations enhance the user experience and provide additional functionality to support fundraising efforts.

In the demo, these integrations are omitted for simplicity.

## User interface

The codebase uses Tailwind + DaisyUI for styling. The style is basic and accessible, mostly mouse-first.
