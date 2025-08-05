import { useMemo } from 'react';
import { 
  getCurrentUser, 
  canManageEntity, 
  isAuthenticated,
  ENTITY_PERMISSIONS 
} from '../utils/permissions';

export const usePermissions = () => {
  const currentUser = getCurrentUser();
  
  const permissions = useMemo(() => {
    if (!currentUser) {
      return {
        isAuthenticated: false,
        canManageUsers: false,
        canManageExperiments: false,
        canManageMeasurements: false,
        canManageTags: false,
        canManageRadioisotopes: false,
        canManageDetectors: false,
        user: null,
        role: null
      };
    }

    return {
      isAuthenticated: isAuthenticated(),
      canManageUsers: canManageEntity('users'),
      canManageExperiments: canManageEntity('experiments'),
      canManageMeasurements: canManageEntity('measurements'),
      canManageTags: canManageEntity('tags'),
      canManageRadioisotopes: canManageEntity('radioisotopes'),
      canManageDetectors: canManageEntity('detectors'),
      user: currentUser,
      role: currentUser.role
    };
  }, [currentUser?.id, currentUser?.role]);

  return permissions;
};

/**
 * Hook for checking specific entity permissions
 * @param {string} entityType - The entity type to check permissions for
 */
export const useEntityPermissions = (entityType) => {
  const currentUser = getCurrentUser();
  
  const permissions = useMemo(() => {
    if (!currentUser || !ENTITY_PERMISSIONS.hasOwnProperty(entityType)) {
      return {
        canView: isAuthenticated(),
        canCreate: false,
        canEdit: false,
        canDelete: false
      };
    }

    const canManage = canManageEntity(entityType);
    
    return {
      canView: isAuthenticated(),
      canCreate: canManage,
      canEdit: canManage,
      canDelete: canManage
    };
  }, [currentUser?.id, currentUser?.role, entityType]);

  return permissions;
};
