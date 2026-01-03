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

Donors can create a group of supporters to pool their resources and make larger contributions, create campaigns and events related to such campaigns, and share campaigns on social media to increase visibility. Donor groups can also track their contributions and the impact of their donations. Donor groups can recruit new members to join their cause.

## Campaigns

Campaigns are the core feature of the platform. Campaigns can be created by the fundraisers, or by a donor group on behalf of a fundraiser. Each campaign includes:

- A title and description of the cause or need.
- A fundraising goal amount.
- An end date for the campaign.
- Updates and progress reports from the fundraiser.

Donors can search and filter campaigns based on categories, popularity, and urgency.

Each campaign page displays the total amount raised, the number of donors, and a progress bar showing how close the campaign is to reaching its goal.

## Events

Events can be created to promote campaigns and encourage donations. Events are linked to specific campaigns and can include:

- Event title and description.
- Date, time, and location of the event.
- A link to the associated campaign.

## Donations

Donors can contribute funds to campaigns through a secure payment system. The platform supports various payment methods, including credit/debit cards and digital wallets. Donors can choose to make one-time donations or set up recurring contributions.

Each donation is tracked and displayed publicly on the campaign page, along with the donor's name (if they choose to be recognized). All amounts raised are transparently shown, along with the remaining amount needed to reach the goal.

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
