import React, { useState } from 'react';
import { Container, AppBar, Toolbar, Typography, Box, CssBaseline } from '@mui/material';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import ResumeParser from './components/ResumeParser';
import JobChatbot from './components/JobChatbot';
import './App.css';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
    background: {
      default: '#f5f5f5',
    },
  },
});

function App() {
  const [resumeData, setResumeData] = useState(null);
  const [sessionId, setSessionId] = useState(null);

  const handleResumeParsed = (data, session) => {
    setResumeData(data);
    setSessionId(session);
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <div className="App">
        <AppBar position="static">
          <Toolbar>
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              Resume Job Hunter
            </Typography>
          </Toolbar>
        </AppBar>
        
        <Container maxWidth="lg" sx={{ mt: 4 }}>
          <Box sx={{ mb: 4 }}>
            <Typography variant="h4" gutterBottom>
              AI-Powered Resume Parser & Job Hunter
            </Typography>
            <Typography variant="subtitle1" color="text.secondary">
              Upload your resume, get it parsed automatically, and find matching job opportunities
            </Typography>
          </Box>

          {!resumeData ? (
            <ResumeParser onResumeParsed={handleResumeParsed} />
          ) : (
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
              <JobChatbot 
                resumeData={resumeData} 
                sessionId={sessionId}
                onReset={() => {
                  setResumeData(null);
                  setSessionId(null);
                }}
              />
            </Box>
          )}
        </Container>
      </div>
    </ThemeProvider>
  );
}

export default App;