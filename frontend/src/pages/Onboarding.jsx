import React from 'react';
import { useNavigate } from 'react-router-dom';
import OnboardingFlow from '../components/OnboardingFlow';

const Onboarding = () => {
  const navigate = useNavigate();

  const handleOnboardingComplete = (data) => {
    console.log('Datos de onboarding guardados:', data);
    
    // Aquí puedes enviar los datos al backend si lo deseas
    // await api.post('/businesses/setup', data);
    
    // Redirigir al dashboard
    navigate('/dashboard');
  };

  return (
    <OnboardingFlow onComplete={handleOnboardingComplete} />
  );
};

export default Onboarding;
