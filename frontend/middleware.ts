import { clerkMiddleware, createRouteMatcher } from "@clerk/nextjs/server";

const isPublic = createRouteMatcher([
  "/",
  "/sign-in(.*)",
  "/sign-up(.*)",
  "/api/webhooks(.*)",
]);

export default clerkMiddleware(
  async (auth, req) => {
    if (!isPublic(req)) {
      await auth().protect();
    }
  },
  {
    authorizedParties: [
      "https://saas-application-saas.up.railway.app",
      "https://saas-application-u2pt.vercel.app",
      "http://localhost:3000",
    ],
  }
);

export const config = {
  matcher: ["/((?!_next|.*\\..*).*)", "/(api|trpc)(.*)"],
};