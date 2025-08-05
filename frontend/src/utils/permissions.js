
const ROLES = {
  USER: 0,
  SHIFTER: 1,
  COORDINATOR: 2,
  ADMIN: 4
};

const ENTITY_PERMISSIONS = {
  users: 'ADMIN',
  experiments: 'COORDINATOR', 
  measurements: 'SHIFTER',
  tags: 'SHIFTER',
  radioisotopes: 'SHIFTER',
  detectors: null // null means any authenticated user
};

export { ENTITY_PERMISSIONS };

let cachedUser = null;
let cacheTimestamp = 0;
const CACHE_DURATION = 5000;

export const getCurrentUser = () => {
  const now = Date.now();
  
  if (cachedUser && (now - cacheTimestamp < CACHE_DURATION)) {
    return cachedUser;
  }
  
  try {
    const user = localStorage.getItem("user");
    cachedUser = user ? JSON.parse(user) : null;
    cacheTimestamp = now;
    return cachedUser;
  } catch (error) {
    console.error("Error parsing user data:", error);
    cachedUser = null;
    return null;
  }
};

export const clearUserCache = () => {
  cachedUser = null;
  cacheTimestamp = 0;
};

export const getUserRoleValue = (role) => {
  if (!role) return ROLES.USER;
  const roleUpper = role.toUpperCase();
  return ROLES[roleUpper] || ROLES.USER;
};

export const hasMinimumRole = (requiredRole) => {
  const currentUser = getCurrentUser();
  if (!currentUser) return false;
  
  const userRoleValue = getUserRoleValue(currentUser.role);
  const requiredRoleValue = getUserRoleValue(requiredRole);
  
  return userRoleValue >= requiredRoleValue;
};

// Generic permission checker - optimized and centralized
export const canManageEntity = (entityType) => {
  const requiredRole = ENTITY_PERMISSIONS[entityType];
  
  // Special case for detectors - any authenticated user
  if (requiredRole === null) {
    return isAuthenticated();
  }
  
  return hasMinimumRole(requiredRole);
};

// Convenience functions that use the centralized logic
export const canManageUsers = () => canManageEntity('users');
export const canManageExperiments = () => canManageEntity('experiments');
export const canManageMeasurements = () => canManageEntity('measurements');
export const canManageTags = () => canManageEntity('tags');
export const canManageRadioisotopes = () => canManageEntity('radioisotopes');
export const canManageDetectors = () => canManageEntity('detectors');

export const isAuthenticated = () => {
  const user = getCurrentUser();
  const token = localStorage.getItem("token");
  return !!(user && token);
};

export const canAccessRoute = (route) => {
  if (route.startsWith('/users')) {
    return canManageUsers();
  }
  
  const routePattern = /\/([^\/]+)\/(?:new|[^\/]+\/edit)$/;
  const match = route.match(routePattern);
  
  if (match) {
    const entityType = match[1];
    
    if (route.includes('/measurements/')) {
      return canManageMeasurements();
    }
    
    if (ENTITY_PERMISSIONS.hasOwnProperty(entityType)) {
      return canManageEntity(entityType);
    }
  }
  
  return isAuthenticated();
};

export default {
  getCurrentUser,
  clearUserCache,
  getUserRoleValue,
  hasMinimumRole,
  canManageEntity,
  canManageUsers,
  canManageExperiments,
  canManageMeasurements,
  canManageTags,
  canManageRadioisotopes,
  canManageDetectors,
  isAuthenticated,
  canAccessRoute,
  ENTITY_PERMISSIONS
};
