import { lazy, Suspense } from "react";
import { createBrowserRouter } from "react-router-dom";
import MainLayout from "../layouts/MainLayout";
import ProtectedRoute from "../components/auth/ProtectedRoute";
import Skeleton from "../components/common/Skeleton";

const Home = lazy(() => import("../pages/home/Home"));
const Dashboard = lazy(() => import("../pages/dashboard/Dashboard"));
const Login = lazy(() => import("../pages/auth/Login"));
const Products = lazy(() => import("../pages/products/Products"));
const ProductDetails = lazy(() => import("../pages/products/ProductDetails"));
const Profile = lazy(() => import("../pages/profile/Profile"));
const Analytics = lazy(() => import("../pages/analytics/Analytics"));
const Wishlist = lazy(() => import("../pages/wishlist/Wishlist"));
const BasketOptimizer = lazy(() => import("../pages/basket/BasketOptimizer"));
const NotFound = lazy(() => import("../pages/NotFound"));

function Lazy({ children }) {
  return (
    <Suspense fallback={<Skeleton className="h-64 w-full" />}>
      {children}
    </Suspense>
  );
}

function guard(el) {
  return (
    <ProtectedRoute>
      <Lazy>{el}</Lazy>
    </ProtectedRoute>
  );
}

export const router = createBrowserRouter([
  {
    path: "/",
    element: <MainLayout />,
    children: [
      { index: true, element: guard(<Home />) },
      { path: "dashboard", element: guard(<Dashboard />) },
      { path: "products", element: guard(<Products />) },
      { path: "products/:id", element: guard(<ProductDetails />) },
      { path: "analytics", element: guard(<Analytics />) },
      { path: "wishlist", element: guard(<Wishlist />) },
      { path: "basket", element: guard(<BasketOptimizer />) },
      { path: "profile", element: guard(<Profile />) },
    ],
  },
  {
    path: "/login",
    element: (
      <Lazy>
        <Login />
      </Lazy>
    ),
  },
  {
    path: "*",
    element: (
      <Lazy>
        <NotFound />
      </Lazy>
    ),
  },
]);
