---
name: odoo-17-mixins
description: Complete reference for Odoo 17 mixins and useful classes. Covers mail.thread (messaging, chatter, field tracking), mail.activity.mixin (activities), mail.alias.mixin / mail.alias.mixin.optional (email aliases), utm.mixin (campaign tracking), portal.mixin (customer portal access), image.mixin / avatar.mixin (images and avatars) and rating.mixin (customer ratings).
globs: "**/models/**/*.py"
topics:
  - mail.thread (messaging, chatter, followers, tracking)
  - mail.activity.mixin (activities)
  - mail.alias.mixin and mail.alias.mixin.optional (email aliases)
  - utm.mixin (campaign tracking)
  - portal.mixin (customer portal access)
  - image.mixin and avatar.mixin (image/avatar)
  - rating.mixin (customer ratings)
when_to_use:
  - Adding messaging/chatter to models
  - Setting up email aliases
  - Adding activities to models
  - Tracking marketing campaigns
  - Exposing records to customer portal
  - Adding images or avatars to records
  - Implementing customer ratings
---

# Odoo 17 Mixins Guide

Complete reference for Odoo 17 mixins: messaging, activities, email aliases, tracking, portal, image/avatar and ratings.

## Table of Contents

1. [mail.thread - Messaging](#mailthread---messaging)
2. [mail.activity.mixin - Activities](#mailactivitymixin---activities)
3. [mail.alias.mixin / mail.alias.mixin.optional - Email Aliases](#mailaliasmixin--mailaliasmixinoptional---email-aliases)
4. [utm.mixin - Campaign Tracking](#utmmixin---campaign-tracking)
5. [portal.mixin - Customer Portal](#portalmixin---customer-portal)
6. [image.mixin / avatar.mixin - Images and Avatars](#imagemixin--avatarmixin---images-and-avatars)
7. [rating.mixin - Customer Ratings](#ratingmixin---customer-ratings)
8. [Mixin Composition](#mixin-composition)

---

## mail.thread - Messaging

### Basic Integration

The `mail.thread` mixin provides chatter, followers, messages, and field tracking.

```python
from odoo import models, fields


class BusinessTrip(models.Model):
    _name = 'business.trip'
    _inherit = ['mail.thread']
    _description = 'Business Trip'

    name = fields.Char(required=True, tracking=True)
    partner_id = fields.Many2one('res.partner', string='Responsible', tracking=True)
    state = fields.Selection(
        [('draft', 'Draft'), ('confirmed', 'Confirmed'), ('done', 'Done')],
        default='draft', tracking=True,
    )
    note = fields.Html()
```

### Form View Integration (Odoo 17)

Odoo 17 uses the classic `div.oe_chatter` structure (the `<chatter>` shortcut tag was introduced in Odoo 18).

```xml
<record id="business_trip_form" model="ir.ui.view">
    <field name="name">business.trip.form</field>
    <field name="model">business.trip</field>
    <field name="arch" type="xml">
        <form string="Business Trip">
            <sheet>
                <group>
                    <field name="name"/>
                    <field name="partner_id"/>
                    <field name="state"/>
                </group>
            </sheet>
            <div class="oe_chatter">
                <field name="message_follower_ids"/>
                <field name="activity_ids"/>
                <field name="message_ids"/>
            </div>
        </form>
    </field>
</record>
```

### Fields Added by mail.thread

| Field | Type | Description |
|-------|------|-------------|
| `message_follower_ids` | One2many | Followers of the record |
| `message_partner_ids` | Many2many | Followers expressed as partners |
| `message_ids` | One2many | Posted messages |
| `message_is_follower` | Boolean | Is current user a follower? |
| `message_has_error` | Boolean | Any failed notifications? |
| `message_attachment_count` | Integer | Attachment count |
| `message_main_attachment_id` | Many2one | Main attachment |

### Field Tracking

Add `tracking=True` to log changes in the chatter automatically. Passing an integer sets the display order in the tracking table.

```python
class BusinessTrip(models.Model):
    _name = 'business.trip'
    _inherit = ['mail.thread']

    name = fields.Char(tracking=True)
    # tracking with explicit order (smaller integer = appears first)
    state = fields.Selection([...], tracking=10)
    partner_id = fields.Many2one('res.partner', tracking=20)
    amount = fields.Monetary(tracking=30)
```

Any change to a tracked field is automatically logged in the chatter with the old and new values.

### Controlling Messaging Access: `_mail_post_access`

The model attribute `_mail_post_access` controls which ACL operation is required to post a message. Default is `'write'`.

```python
class PublicThread(models.Model):
    _name = 'public.thread'
    _inherit = ['mail.thread']

    # Anyone with read access can post a message
    _mail_post_access = 'read'
```

Valid values: `'read'`, `'write'`, `'create'`, `'unlink'`.

### Posting Messages

#### message_post() - Main API

```python
def notify_confirmation(self):
    self.ensure_one()
    self.message_post(
        body='Trip has been confirmed!',
        subject='Trip Confirmation',
        message_type='comment',              # 'comment', 'notification', 'email'
        subtype_xmlid='mail.mt_comment',     # or 'mail.mt_note' for internal log
        partner_ids=[self.partner_id.id],    # extra recipients (list of IDs)
        author_id=self.env.user.partner_id.id,
    )
```

Key keyword arguments (all keyword-only in v17):

| Argument | Description |
|----------|-------------|
| `body` | `str` (auto-escaped) or `markupsafe.Markup` for HTML |
| `subject` | Optional subject |
| `message_type` | `'notification'` (default), `'comment'`, `'email'`; NOT `'user_notification'` |
| `subtype_xmlid` | XML id of the subtype, e.g. `'mail.mt_comment'`, `'mail.mt_note'` |
| `subtype_id` | Alternative to `subtype_xmlid` |
| `partner_ids` | Extra partner IDs to notify (list of integers) |
| `author_id` | Partner ID of the author |
| `email_from` | Author email (used when author_id is unknown) |
| `parent_id` | Parent message for threading |
| `attachment_ids` | List of existing `ir.attachment` IDs |
| `attachments` | List of `(name, content)` or `(name, content, info)` tuples |

#### Posting with Markup (HTML)

```python
from markupsafe import Markup


def notify_html(self):
    body = Markup("<p>Status changed to <b>%s</b></p>") % self.state
    self.message_post(body=body, subtype_xmlid='mail.mt_note')
```

Never build HTML via f-strings: use `Markup(...) % value` or `Markup(...).format(value=...)` so user content is escaped.

#### Posting with Attachments

```python
def attach_report(self, pdf_content):
    self.message_post(
        body='Report attached',
        attachments=[('report.pdf', pdf_content)],
    )
```

#### Sending via a Template

In Odoo 17 the helper is `message_post_with_source` (the former `message_post_with_template` was removed in Odoo 17):

```python
def send_template(self):
    self.message_post_with_source(
        'my_module.email_template_trip_confirmation',
        subtype_xmlid='mail.mt_comment',
    )
```

### Followers Management

```python
# Add partners as followers
record.message_subscribe(partner_ids=[partner1.id, partner2.id])

# Add with a specific subtype
record.message_subscribe(
    partner_ids=[partner.id],
    subtype_ids=[self.env.ref('mail.mt_comment').id],
)

# Remove
record.message_unsubscribe(partner_ids=[partner.id])
```

### Subtypes and `_track_subtype`

Subtypes classify notifications so users can filter what they receive.

Define a subtype in XML:

```xml
<record id="mt_trip_confirmed" model="mail.message.subtype">
    <field name="name">Trip Confirmed</field>
    <field name="res_model">business.trip</field>
    <field name="default" eval="True"/>
    <field name="description">Business Trip confirmed!</field>
</record>
```

Override `_track_subtype` to emit a custom subtype when a tracked field changes.

**Important (Odoo 17)**: `_track_subtype` must return a `mail.message.subtype` **record** (or `False`), not an XML id string.

```python
class BusinessTrip(models.Model):
    _name = 'business.trip'
    _inherit = ['mail.thread']

    state = fields.Selection(
        [('draft', 'Draft'), ('confirmed', 'Confirmed')], tracking=True,
    )

    def _track_subtype(self, init_values):
        self.ensure_one()
        if 'state' in init_values and self.state == 'confirmed':
            return self.env.ref('my_module.mt_trip_confirmed')
        return super()._track_subtype(init_values)
```

### Context Keys for Control

| Key | Effect |
|-----|--------|
| `mail_create_nosubscribe` | Don't subscribe author on create |
| `mail_create_nolog` | Don't log `"<Document> created"` message |
| `mail_notrack` | Skip field tracking |
| `tracking_disable` | Disable all mail.thread features (tracking + logging + subscription) |
| `mail_auto_delete` | Auto-delete notifications (default `True`) |
| `mail_notify_force_send` | Send mails directly instead of queuing |

```python
self.env['business.trip'].with_context(
    tracking_disable=True,
).create({'name': 'Silent Trip'})
```

### Incoming Mail Hooks (when combined with alias)

```python
def message_new(self, msg_dict, custom_values=None):
    """Create a record from an incoming email."""
    defaults = {
        'name': msg_dict.get('subject') or 'Incoming',
        'email_from': msg_dict.get('from'),
    }
    if custom_values:
        defaults.update(custom_values)
    return super().message_new(msg_dict, defaults)


def message_update(self, msg_dict, update_vals=None):
    """Update an existing record from a reply."""
    return super().message_update(msg_dict, update_vals)
```

---

## mail.activity.mixin - Activities

The `mail.activity.mixin` adds an `activity_ids` one2many and helper fields/methods to schedule tasks on records (calls, meetings, to-dos, etc.).

### Integration

```python
class BusinessTrip(models.Model):
    _name = 'business.trip'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Business Trip'

    name = fields.Char(required=True)
```

### Form View Integration

```xml
<div class="oe_chatter">
    <field name="message_follower_ids"/>
    <field name="activity_ids"/>
    <field name="message_ids"/>
</div>
```

### Kanban Integration

```xml
<kanban>
    <field name="activity_ids"/>
    <field name="activity_state"/>
    <templates>
        <t t-name="kanban-box">
            <div>
                <field name="name"/>
                <div class="oe_kanban_bottom_right">
                    <field name="activity_ids" widget="kanban_activity"/>
                </div>
            </div>
        </t>
    </templates>
</kanban>
```

### Fields Added

| Field | Description |
|-------|-------------|
| `activity_ids` | One2many on `mail.activity` |
| `activity_state` | `'overdue'`, `'today'`, `'planned'` or `False` |
| `activity_user_id` | Responsible of the next activity |
| `activity_type_id` | Next activity type |
| `activity_date_deadline` | Next deadline |
| `my_activity_date_deadline` | Next deadline for the current user |
| `activity_summary` | Summary of the next activity |

### Scheduling Activities

```python
from datetime import date, timedelta


def plan_review(self):
    self.activity_schedule(
        'mail.mail_activity_data_todo',
        user_id=self.env.user.id,
        summary='Review trip',
        note='<p>Please review and approve</p>',
        date_deadline=date.today() + timedelta(days=3),
    )


def mark_done(self):
    self.activity_feedback(
        ['mail.mail_activity_data_todo'],
        feedback='Reviewed, looks good',
    )
```

| Method | Description |
|--------|-------------|
| `activity_schedule(act_type_xmlid, date_deadline=None, summary='', note='', **kwargs)` | Create an activity |
| `activity_reschedule(act_type_xmlids, date_deadline=None, new_user_id=None)` | Move/reassign activities |
| `activity_feedback(act_type_xmlids, feedback=None)` | Mark activities as done |
| `activity_unlink(act_type_xmlids)` | Remove activities without feedback |

### Context Keys

| Key | Effect |
|-----|--------|
| `mail_activity_automation_skip` | Skip automated activity generation/update |

---

## mail.alias.mixin / mail.alias.mixin.optional - Email Aliases

Aliases allow creating records by sending an email to a specific address.

### Two Variants

| Mixin | Behaviour |
|-------|-----------|
| `mail.alias.mixin.optional` | `alias_id` is **optional** - created on demand when `alias_name` is set. Uses related fields, not `_inherits`. Good for models where most records have no alias. |
| `mail.alias.mixin` | `alias_id` is **required** - uses `_inherits` so every record has an alias. Extends `mail.alias.mixin.optional`. |

### mail.alias.mixin (required alias, full integration)

```python
from odoo import models, fields


class BusinessTrip(models.Model):
    _name = 'business.trip'
    _inherit = ['mail.thread', 'mail.alias.mixin']
    _description = 'Business Trip'

    name = fields.Char(required=True)
    expense_ids = fields.One2many('business.expense', 'trip_id')

    # alias_id is required through _inherits; these come from the mixin:
    #   alias_name, alias_defaults, alias_domain_id, alias_email, ...

    def _alias_get_creation_values(self):
        """Return the values used when creating the underlying alias."""
        values = super()._alias_get_creation_values()
        values['alias_model_id'] = self.env['ir.model']._get('business.expense').id
        if self.id:
            values['alias_defaults'] = {'trip_id': self.id}
            values['alias_contact'] = 'followers'
        return values
```

### mail.alias.mixin.optional (alias created on demand)

```python
class Team(models.Model):
    _name = 'crm.team'
    _inherit = ['mail.alias.mixin.optional']

    def _alias_get_creation_values(self):
        values = super()._alias_get_creation_values()
        values['alias_model_id'] = self.env['ir.model']._get('crm.lead').id
        if self.id:
            values['alias_defaults'] = {'team_id': self.id}
        return values
```

### Form View

```xml
<group string="Email Alias">
    <field name="alias_name"/>
    <field name="alias_domain" readonly="1"/>
    <field name="alias_contact"/>
    <field name="alias_defaults" invisible="1"/>
</group>
```

### Alias Configuration Fields

| Field | Description |
|-------|-------------|
| `alias_name` | Local part of the email (e.g. `jobs` for `jobs@example.com`) |
| `alias_domain_id` | Alias domain record (Odoo 17 multi-domain support) |
| `alias_domain` | Domain name (related, read-only) |
| `alias_email` | Computed `alias_name@alias_domain` |
| `alias_defaults` | Python dict literal of default values applied to created records |
| `alias_contact` | `'everyone'`, `'partners'`, `'followers'` |
| `alias_force_thread_id` | Force incoming mails into this thread ID |

### Writable Fields (mail.alias.mixin.optional)

Only these alias fields can be written through the mixin:

```python
ALIAS_WRITEABLE_FIELDS = [
    'alias_domain_id', 'alias_name', 'alias_contact',
    'alias_defaults', 'alias_bounced_content',
]
```

---

## utm.mixin - Campaign Tracking

Track marketing campaigns through URL parameters.

```python
from odoo import models, fields


class Lead(models.Model):
    _name = 'crm.lead'
    _inherit = ['utm.mixin']

    name = fields.Char()
```

### Fields Added

| Field | Type | Cookie |
|-------|------|--------|
| `campaign_id` | Many2one `utm.campaign` | `odoo_utm_campaign` |
| `source_id` | Many2one `utm.source` | `odoo_utm_source` |
| `medium_id` | Many2one `utm.medium` | `odoo_utm_medium` |

### How It Works

1. User clicks `https://myodoo.com/?utm_campaign=winter_sale&utm_source=google`
2. `ir_http` stores the URL parameters in cookies
3. `default_get` on the UTM mixin reads those cookies and populates the fields when a record is created (e.g. via a website form)

### Adding Custom Tracking

```python
class MyModel(models.Model):
    _name = 'my.model'
    _inherit = ['utm.mixin']

    my_source = fields.Many2one('utm.source', string='Custom Source')

    @api.model
    def tracking_fields(self):
        """Must be called as self.env['utm.mixin'].tracking_fields()."""
        result = super().tracking_fields()
        result.append(('utm_my_source', 'my_source', 'odoo_utm_my_source'))
        return result
```

---

## portal.mixin - Customer Portal

Expose records to external partners through the customer portal with a signed access URL.

```python
from odoo import models, fields


class SaleOrder(models.Model):
    _name = 'sale.order'
    _inherit = ['portal.mixin', 'mail.thread']

    partner_id = fields.Many2one('res.partner', required=True)

    def _compute_access_url(self):
        super()._compute_access_url()
        for order in self:
            order.access_url = f'/my/orders/{order.id}'
```

### Fields Added

| Field | Description |
|-------|-------------|
| `access_url` | Portal URL of the record (must be computed by the model) |
| `access_token` | Signed token to access the record without login |
| `access_warning` | Optional warning message shown on the portal |

### Methods

| Method | Description |
|--------|-------------|
| `_portal_ensure_token()` | Generate/return the record's access token |
| `_get_share_url(redirect=False, signup_partner=False, pid=None)` | Build the full share URL with token |
| `_get_access_action(access_uid=None, force_website=False)` | Returns the action that opens the record for a portal user |
| `_get_access_warning()` | Override to emit a custom warning shown on the portal page |

### Building a Share Link

```python
def action_share(self):
    self.ensure_one()
    return {
        'type': 'ir.actions.act_url',
        'url': self._get_share_url(),
        'target': 'new',
    }
```

---

## image.mixin / avatar.mixin - Images and Avatars

### image.mixin

Stores an image with automatically-resized variants (1920, 1024, 512, 256, 128).

```python
from odoo import models, fields


class Product(models.Model):
    _name = 'my.product'
    _inherit = ['image.mixin']

    name = fields.Char()
```

Fields added:

| Field | Max Size |
|-------|----------|
| `image_1920` | 1920 px (base) |
| `image_1024` | 1024 px (related, stored) |
| `image_512` | 512 px (related, stored) |
| `image_256` | 256 px (related, stored) |
| `image_128` | 128 px (related, stored) |

Form view usage:

```xml
<field name="image_1920" widget="image" options="{'preview_image': 'image_128'}"/>
```

### avatar.mixin

Extends `image.mixin` with auto-generated SVG avatars (initial + colour) when no image is uploaded.

```python
class Team(models.Model):
    _name = 'team'
    _inherit = ['avatar.mixin']
    _avatar_name_field = 'name'  # defaults to 'name'

    name = fields.Char(required=True)
```

Fields added (on top of `image.mixin`):

| Field | Description |
|-------|-------------|
| `avatar_1920..avatar_128` | Either the uploaded image or a generated SVG (initial letter on a seeded HSL background) |

Override `_avatar_name_field` if the initial should come from another field, or `_avatar_get_placeholder_path()` for a custom fallback PNG.

---

## rating.mixin - Customer Ratings

Receive and aggregate ratings (1-5) from customers. The mixin **inherits `mail.thread`** automatically - you do not need to add it again.

```python
from odoo import models, fields


class ProjectTask(models.Model):
    _name = 'project.task'
    _inherit = ['rating.mixin']           # inherits mail.thread
    _description = 'Task'

    name = fields.Char()
    user_id = fields.Many2one('res.users')
    partner_id = fields.Many2one('res.partner')
```

### Fields Added

| Field | Description |
|-------|-------------|
| `rating_ids` | All ratings on this record |
| `rating_count` | Number of consumed ratings |
| `rating_avg` | Average rating (out of 5) |
| `rating_avg_text` | Text version (`'Dissatisfied'`, `'Okay'`, `'Satisfied'`) |
| `rating_last_value` | Last rating value |
| `rating_last_feedback` | Last rating text feedback |
| `rating_last_image` | Smiley image for the last rating |
| `rating_percentage_satisfaction` | % of ratings >= threshold |

### Identifying the Rater and the Rated

By default the mixin uses `partner_id` (customer) as the rater and `user_id` (assignee) as the person rated. Override if different:

```python
def _rating_get_partner(self):
    """Partner giving the rating (customer)."""
    return self.customer_id or super()._rating_get_partner()


def _rating_get_rated_partner(self):
    """Partner being rated (internal user)."""
    return self.assignee_id.partner_id or super()._rating_get_rated_partner()
```

### Sending a Rating Request

```python
def send_rating_request(self):
    self.ensure_one()
    self.rating_send_request(
        rating_template=self.env.ref('my_module.rating_request_email'),
        reuse_rating=False,
        force_send=True,
    )
```

### Portal Rating Link

```python
def rating_portal_link(self, value):
    """Build /rate/<token>/<value> URL."""
    return f'/rate/{self.rating_get_access_token()}/{value}'
```

---

## Mixin Composition

Stack mixins in `_inherit` to compose behaviour. Order is usually bottom-up (more specific first), but the mail mixins tolerate any order.

### Typical Document Model

```python
class BusinessTrip(models.Model):
    _name = 'business.trip'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Business Trip'

    name = fields.Char(required=True, tracking=True)
    state = fields.Selection(
        [('draft', 'Draft'), ('confirmed', 'Confirmed'), ('done', 'Done')],
        default='draft', tracking=True,
    )
```

### Document + Alias + Activities

```python
class HelpdeskTeam(models.Model):
    _name = 'helpdesk.team'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'mail.alias.mixin.optional']
```

### Portal-Visible Document

```python
class SaleOrder(models.Model):
    _name = 'sale.order'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
```

### CRM-style Rated Document

```python
class Lead(models.Model):
    _name = 'crm.lead'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'utm.mixin', 'rating.mixin']
    # rating.mixin already brings mail.thread; listing it explicitly is fine.
```

### Visual Product with Avatar

```python
class Team(models.Model):
    _name = 'team'
    _inherit = ['avatar.mixin', 'mail.thread']
```

---

## Quick Reference

### Mixin Summary

| Mixin | Purpose | Key Fields |
|-------|---------|------------|
| `mail.thread` | Messaging, followers, tracking | `message_ids`, `message_follower_ids` |
| `mail.activity.mixin` | Activities | `activity_ids`, `activity_state` |
| `mail.alias.mixin` | Required email alias | `alias_id`, `alias_name`, `alias_domain_id` |
| `mail.alias.mixin.optional` | Optional email alias | Same as above, `alias_id` optional |
| `utm.mixin` | Marketing tracking | `campaign_id`, `source_id`, `medium_id` |
| `portal.mixin` | Portal URL + token | `access_url`, `access_token` |
| `image.mixin` | Image with variants | `image_1920/1024/512/256/128` |
| `avatar.mixin` | Auto-generated avatars | `avatar_1920/1024/512/256/128` |
| `rating.mixin` | Customer ratings (+ mail.thread) | `rating_ids`, `rating_avg` |

### Messaging Cheatsheet

```python
# Post a note (internal log, only followers)
self.message_post(body='Internal note', subtype_xmlid='mail.mt_note')

# Post a public comment (sends emails)
self.message_post(
    body='Hello!',
    subtype_xmlid='mail.mt_comment',
    partner_ids=[partner.id],
)

# Subscribe someone
self.message_subscribe(partner_ids=[partner.id])

# Schedule an activity
self.activity_schedule(
    'mail.mail_activity_data_todo',
    summary='Review',
    user_id=self.env.user.id,
)
```

---

## Base Code Reference

The guide is based on the Odoo 17 source tree. Reference files:

| File | Contents |
|------|----------|
| `addons/mail/models/mail_thread.py` | `mail.thread`, `message_post`, `_track_subtype`, `_mail_post_access` |
| `addons/mail/models/mail_activity_mixin.py` | `mail.activity.mixin` and activity helpers |
| `addons/mail/models/mail_alias_mixin.py` | Required-alias mixin (`_inherits` on `mail.alias`) |
| `addons/mail/models/mail_alias_mixin_optional.py` | Optional-alias mixin (on-demand creation) |
| `addons/utm/models/utm_mixin.py` | UTM fields and cookie mapping |
| `addons/portal/models/portal_mixin.py` | Portal URL + access token |
| `odoo/addons/base/models/image_mixin.py` | Image variants |
| `odoo/addons/base/models/avatar_mixin.py` | Generated SVG avatar |
| `addons/rating/models/rating_mixin.py` | Rating statistics (inherits `mail.thread`) |

**For more Odoo 17 guides, see [SKILL.md](../SKILL.md)**
