/*
 * SSS Import Export — site settings.
 * Fill in the values marked [PLACEHOLDER]. Every phone/WhatsApp/email link
 * on every page is built from this file, so you only edit it once.
 */
window.SSS_CONFIG = {
  // Digits only, with country code, no "+" or spaces. Example format: 919876543210
  whatsappNumber: '[WHATSAPP_NUMBER]',
  // Shown as text, e.g. "+91 98765 43210"
  phoneDisplay: '[PHONE_NUMBER]',
  // Digits with country code for tel: links, e.g. +919876543210
  phoneDial: '[PHONE_DIAL]',
  email: '[EMAIL]',
  address: '[ADDRESS]',
  instagram: 'sssimportexport',

  // Optional: a form endpoint (Formspree, Web3Forms, Getform, etc.) for the quote form.
  // Leave as-is and the form will open WhatsApp with the enquiry pre-filled instead.
  formEndpoint: '[FORM_ENDPOINT]'
};
