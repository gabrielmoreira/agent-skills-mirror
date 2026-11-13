export interface Customer {
  id: number;
  name: string;
  email?: string;
  phone?: string;
  // sales
  isLead?: boolean;
  leadScore?: number;
  accountManagerId?: number;
  quoteDiscountPct?: number;
  signedQuoteId?: number;
  crmExternalId?: string;
  // billing
  stripeCustomerId?: string;
  billingAddress?: string;
  vatNumber?: string;
  paymentTermsDays?: number;
  creditLimitCents?: number;
  dunningLevel?: number;
  // fulfillment
  shippingAddress?: string;
  deliveryWindow?: string;
  dockInstructions?: string;
  carrierAccount?: string;
  isWarehouse?: boolean;
  parentCustomerId?: number;
  status: number; // 0 lead, 1 trial, 2 active, 3 on hold, 4 closed
}
