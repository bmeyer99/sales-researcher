// Environment variables should be accessed via this config file
// to centralize their usage and make it easier to manage.

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL;
export const GOOGLE_CLIENT_ID = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID;

if (!API_BASE_URL) {
  console.warn(
    'NEXT_PUBLIC_API_BASE_URL is not defined. API calls may fail.'
  );
}

if (!GOOGLE_CLIENT_ID) {
  console.warn(
    'NEXT_PUBLIC_GOOGLE_CLIENT_ID is not defined. Google OAuth may not work.'
  );
}