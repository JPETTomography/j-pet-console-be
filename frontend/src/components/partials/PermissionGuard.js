import { usePermissions } from '../../hooks/usePermissions';

/**
 * Wrapper component for permission-based rendering
 * More efficient than inline permission checks
 */
const PermissionGuard = ({ 
  children, 
  entityType, 
  action = 'manage', 
  fallback = null,
  showDisabled = false 
}) => {
  const permissions = usePermissions();
  
  let hasPermission = false;
  
  switch (entityType) {
    case 'users':
      hasPermission = permissions.canManageUsers;
      break;
    case 'experiments':
      hasPermission = permissions.canManageExperiments;
      break;
    case 'measurements':
      hasPermission = permissions.canManageMeasurements;
      break;
    case 'tags':
      hasPermission = permissions.canManageTags;
      break;
    case 'radioisotopes':
      hasPermission = permissions.canManageRadioisotopes;
      break;
    case 'detectors':
      hasPermission = permissions.canManageDetectors;
      break;
    default:
      hasPermission = permissions.isAuthenticated;
  }
  
  if (!hasPermission) {
    if (showDisabled && typeof children === 'function') {
      return children({ disabled: true });
    }
    return fallback;
  }
  
  if (typeof children === 'function') {
    return children({ disabled: false });
  }
  
  return children;
};

export default PermissionGuard;
