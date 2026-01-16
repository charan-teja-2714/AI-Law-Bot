import React from 'react';

function RoleToggle({ role, onChange }) {
  return (
    <select 
      value={role} 
      onChange={(e) => onChange(e.target.value)}
      className="role-select"
    >
      <option value="patient">Patient (Simple Language)</option>
      <option value="doctor">Doctor (Technical)</option>
    </select>
  );
}

export default RoleToggle;
