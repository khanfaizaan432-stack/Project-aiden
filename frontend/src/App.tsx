import {
  Outlet,
  RouterProvider,
  createRootRoute,
  createRoute,
  createRouter,
  useNavigate,
  useParams,
} from "@tanstack/react-router";
import { AgentDetail } from "./pages/AgentDetail";
import { Dashboard } from "./pages/Dashboard";

export { useNavigate, useParams };

const rootRoute = createRootRoute({
  component: () => <Outlet />,
});

const indexRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/",
  component: Dashboard,
});

const agentDetailRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/agent/$id",
  component: AgentDetail,
});

const routeTree = rootRoute.addChildren([indexRoute, agentDetailRoute]);

const router = createRouter({ routeTree });

declare module "@tanstack/react-router" {
  interface Register {
    router: typeof router;
  }
}

export default function App() {
  return <RouterProvider router={router} />;
}
