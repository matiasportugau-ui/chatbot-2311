# Shopify Webhooks via Google Cloud Pub/Sub

## About webhooks

When your app needs information about specific events that have occurred on a shop, it can subscribe to Shopify webhook topics as a mechanism for receiving near-real-time data about these events.

Shopify webhooks are useful for keeping your app in sync with Shopify data, or as a trigger to perform an additional action after that event has occurred. They are also a performant alternative to continuously polling for changes to a shop's data.

This guide provides a quick primer on when to use APIs versus webhooks, as well as key terminology and behaviors that are specific to Shopify webhooks.

### Examples of when your app might use webhooks

* Sending notifications about changes in inventory levels to inventory management clients and pagers
* Informing shipping companies about changes in orders, returns, or refunds
* Removing customer data from a database for app uninstalls
* Integrating data about orders with accounting software
* Updating a product's warranty price based on changes to the product's price

***

## APIs for continuous polling vs. Webhooks for events data

The following example uses the `orders/create` webhook topic to illustrate the difference between polling an API for data about events, versus subscribing to a webhook topic to receive data about events.

1. The app subscribes to the `orders/create` topic for a shop and listens for order creation events.
2. The app specifies an endpoint to receive webhooks for the `orders/create` topic.
3. Suppose now that an order is created from that shop.
4. This triggers a webhook to be published to the `orders/create` topic.
5. Shopify sends that webhook, which includes headers and an order payload, to the specified subscription endpoint.

***

## Key terminology

### Webhook topic

The **webhook topic** defines the kind of event messages that your app receives. For example, your app can subscribe to the `products/create` topic to be notified about new products that are created.

### Webhook subscription

A **webhook subscription** declares the app’s intention to receive webhooks for a topic. A subscription is defined by:
* The topic name
* The subscription endpoint (e.g., Google Pub/Sub)

Shopify recommends using Google Pub/Sub whenever possible.

### Headers

Each webhook is made up of **headers** and a **payload**.

Example headers:
```sh
X-Shopify-Topic: `orders/create`
X-Shopify-Shop-Domain: `{shop}.myshopify.com`
X-Shopify-API-Version: `2025-10`
X-Shopify-Webhook-Id: `b54557e4-bdd9-4b37-8a5f-bf7d70bcd043`
X-Shopify-Triggered-At: `2023-03-29T18:00:27.877041743Z`
```

> [!CAUTION]
> Webhook header names are case-insensitive. Your app should treat `X-Shopify-Topic` and `x-shopify-topic` interchangeably.

When using Google Cloud Pub/Sub, you receive a JSON payload that wraps the Shopify event data.

***

## What to expect when working with Shopify event data

### Ordering event data
Shopify doesn't guarantee ordering. Use `X-Shopify-Triggered-At` or payload timestamps (`updated_at`) to organize events.

### Handling duplicate webhooks
Your app may receive duplicates. Compare `X-Shopify-Event-Id` to detect them.

***

## Setup Instructions

### 1. Google Cloud Setup

1.  **Create a Topic**:
    *   Go to the Google Cloud Console -> Pub/Sub -> Topics.
    *   Create a new topic (e.g., `shopify-events`).

2.  **Grant Permissions**:
    *   Shopify's service account needs permission to publish to your topic.
    *   Add Principal: `delivery@shopify-pubsub-webhooks.iam.gserviceaccount.com`
    *   Role: `Pub/Sub Publisher`

3.  **Create a Push Subscription**:
    *   Create a subscription for the topic.
    *   Delivery Type: **Push**.
    *   Endpoint URL: `https://<YOUR_APP_DOMAIN>/api/webhooks/shopify`
    *   (Optional) Enable authentication to secure the endpoint.

### 2. Configure Shopify

1.  In your Shopify Partner Dashboard or via Admin API, create a webhook subscription.
2.  Select the Topic (e.g., `products/update`).
3.  Format: `JSON`.
4.  Address: `pubsub://<PROJECT_ID>:<TOPIC_NAME>` (e.g., `pubsub://my-project:shopify-events`).

### 3. Application Code

This project includes a helper to decode the Pub/Sub messages.
See `src/lib/google-pubsub.ts` and `src/app/api/webhooks/shopify/route.ts` for details.

When a message arrives at the endpoint:
1.  The app receives the standard Pub/Sub JSON body.
2.  It decodes the base64 `message.data` field to get the actual Shopify payload.
3.  It logs the event (customize `route.ts` to add business logic).
