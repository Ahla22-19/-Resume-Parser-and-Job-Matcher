import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  Typography,
  TextField,
  CircularProgress,
  Alert,
  Grid,
  Paper,
  Chip,
  Divider,
} 
from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import DescriptionIcon from '@mui/icons-material/Description';
import axios from 'axios';
import { styled } from '@mui/material/styles';

const VisuallyHiddenInput = styled('input')({
  clip: 'rect(0 0 0 0)',
  clipPath: 'inset(50%)',
  height: 1,
  overflow: 'hidden',
  position: 'absolute',
  bottom: 0,
  left: 0,
  whiteSpace: 'nowrap',
  width: 1,
});

const API_BASE_URL = 'http://localhost:8000';

const ResumeParser = ({ onResumeParsed }) => {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [parsedData, setParsedData] = useState(null);
  const [dragOver, setDragOver] = useState(false);

  // Prevent Chrome from opening PDFs when dropped
  useEffect(() => {
    const preventDefaultBehavior = (e) => {
      e.preventDefault();
      e.stopPropagation();
    };

    // Add event listeners to entire document
    const events = ['dragenter', 'dragover', 'dragleave', 'drop'];
    events.forEach(eventName => {
      document.addEventListener(eventName, preventDefaultBehavior, true);
    });

    // Cleanup
    return () => {
      events.forEach(eventName => {
        document.removeEventListener(eventName, preventDefaultBehavior, true);
      });
    };
  }, []);

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    if (selectedFile) {
      validateAndSetFile(selectedFile);
    }
  };

  const handleDragEnter = (event) => {
    event.preventDefault();
    event.stopPropagation();
    setDragOver(true);
  };

  const handleDragOver = (event) => {
    event.preventDefault();
    event.stopPropagation();
    setDragOver(true);
    
    // Set drop effect to copy
    if (event.dataTransfer) {
      event.dataTransfer.dropEffect = 'copy';
    }
  };

  const handleDragLeave = (event) => {
    event.preventDefault();
    event.stopPropagation();
    setDragOver(false);
  };

  const handleDrop = (event) => {
    event.preventDefault();
    event.stopPropagation();
    setDragOver(false);
    
    const files = event.dataTransfer.files;
    if (files.length > 0) {
      const droppedFile = files[0];
      validateAndSetFile(droppedFile);
      
      // Clear data transfer to prevent Chrome from opening the file
      if (event.dataTransfer) {
        event.dataTransfer.clearData();
      }
    }
  };

  const validateAndSetFile = (selectedFile) => {
    // Check file type by extension (more reliable than MIME type)
    const allowedExtensions = ['.pdf', '.docx', '.txt'];
    const fileExtension = selectedFile.name.toLowerCase().substring(selectedFile.name.lastIndexOf('.'));
    
    // Also check MIME type as fallback
    const allowedMimeTypes = [
      'application/pdf',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'text/plain'
    ];
    
    if (!allowedExtensions.includes(fileExtension) && !allowedMimeTypes.includes(selectedFile.type)) {
      setError('Please upload a PDF, DOCX, or TXT file');
      return;
    }
    
    // Check file size (max 10MB for PDFs)
    if (selectedFile.size > 10 * 1024 * 1024) {
      setError('File size too large. Maximum size is 10MB');
      return;
    }
    
    setFile(selectedFile);
    setError(null);
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file first');
      return;
    }

    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      console.log('Uploading file:', file.name);
      const response = await axios.post(`${API_BASE_URL}/parse-resume`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      console.log('Response received:', response.data);

      if (response.data.success) {
        const data = response.data.data;
        setParsedData(data);
      } else {
        setError(response.data.message || 'Failed to parse resume');
      }
    } catch (err) {
      console.error('Upload error:', err);
      setError(
        err.response?.data?.detail || 
        err.response?.data?.message || 
        err.message || 
        'An error occurred while uploading the file'
      );
    } finally {
      setLoading(false);
    }
  };

  const handleStartJobHunting = async () => {
    if (!parsedData) {
      setError('No parsed data available');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Create session ID
      const sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      console.log('Creating session:', sessionId);
      
      // Create chat agent with resume data
      await axios.post(`${API_BASE_URL}/create-agent/${sessionId}`, parsedData);
      
      // Pass data and session ID to parent component
      onResumeParsed(parsedData, sessionId);
    } catch (agentError) {
      console.error('Error creating agent:', agentError);
      setError('Failed to create chat session. Please try again.');
      setLoading(false);
    }
  };

  const handleReset = () => {
    setFile(null);
    setParsedData(null);
    setError(null);
    setDragOver(false);
  };

  return (
    <Box sx={{ maxWidth: 800, mx: 'auto' }}>
      <Card>
        <CardContent>
          <Typography variant="h5" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <DescriptionIcon /> Resume Parser
          </Typography>
          
          <Typography variant="body2" color="text.secondary" paragraph>
            Upload your resume (PDF or DOCX) to automatically extract your information
          </Typography>

          {!parsedData ? (
            <Box sx={{ mt: 3 }}>
              <Paper
                variant="outlined"
                sx={{
                  p: 4,
                  textAlign: 'center',
                  border: '2px dashed',
                  borderColor: dragOver ? 'primary.main' : '#ccc',
                  backgroundColor: dragOver ? 'action.hover' : 'background.default',
                  cursor: 'pointer',
                  transition: 'all 0.2s',
                  '&:hover': {
                    borderColor: 'primary.main',
                    backgroundColor: 'action.hover',
                  },
                }}
                onClick={() => document.getElementById('resume-upload').click()}
                onDragEnter={handleDragEnter}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
              >
                <CloudUploadIcon sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
                <Typography variant="h6" gutterBottom>
                  {dragOver ? 'Drop your file here!' : 'Drag & drop or click to upload'}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Supported formats: PDF, DOCX, TXT
                </Typography>
                <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1 }}>
                  Max file size: 10MB • For PDFs in Chrome, hold Ctrl key while dropping
                </Typography>
                <VisuallyHiddenInput
                  id="resume-upload"
                  type="file"
                  onChange={handleFileChange}
                  accept=".pdf,.docx,.txt"
                />
              </Paper>

              <Box sx={{ mt: 2, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 1 }}>
                <Typography variant="body2" color="text.secondary">
                  Or select a file:
                </Typography>
                <Button
                  variant="outlined"
                  component="label"
                  startIcon={<CloudUploadIcon />}
                  size="small"
                >
                  Choose File
                  <VisuallyHiddenInput
                    type="file"
                    onChange={handleFileChange}
                    accept=".pdf,.docx,.txt"
                  />
                </Button>
              </Box>

              {file && (
                <Box sx={{ mt: 2, p: 2, bgcolor: 'success.light', borderRadius: 1 }}>
                  <Typography variant="body2">
                    Selected: <strong>{file.name}</strong> ({Math.round(file.size / 1024)} KB)
                  </Typography>
                </Box>
              )}

              {error && (
                <Alert 
                  severity="error" 
                  sx={{ mt: 2 }}
                  onClose={() => setError(null)}
                >
                  {error}
                </Alert>
              )}

              <Box sx={{ mt: 3, display: 'flex', gap: 2, justifyContent: 'center' }}>
                <Button
                  variant="contained"
                  onClick={handleUpload}
                  disabled={!file || loading}
                  startIcon={loading ? <CircularProgress size={20} /> : null}
                  size="large"
                >
                  {loading ? 'Parsing...' : 'Parse Resume'}
                </Button>
                
                {file && (
                  <Button variant="outlined" onClick={handleReset}>
                    Reset
                  </Button>
                )}
              </Box>
            </Box>
          ) : (
            <Box sx={{ mt: 2 }}>
              <Alert severity="success" sx={{ mb: 3 }}>
                Resume parsed successfully! Your information has been extracted.
              </Alert>

              <Grid container spacing={3}>
                <Grid item xs={12}>
                  <Typography variant="h6" gutterBottom>
                    Personal Information
                  </Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={12} sm={6}>
                      <TextField
                        fullWidth
                        label="Full Name"
                        value={parsedData.name || ''}
                        variant="outlined"
                        InputProps={{ readOnly: true }}
                      />
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <TextField
                        fullWidth
                        label="Email"
                        value={parsedData.email || ''}
                        variant="outlined"
                        InputProps={{ readOnly: true }}
                      />
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <TextField
                        fullWidth
                        label="Phone"
                        value={parsedData.phone || ''}
                        variant="outlined"
                        InputProps={{ readOnly: true }}
                      />
                    </Grid>
                  </Grid>
                </Grid>

                <Grid item xs={12}>
                  <Divider sx={{ my: 2 }} />
                  <Typography variant="h6" gutterBottom>
                    Skills
                  </Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                    {parsedData.skills && parsedData.skills.length > 0 ? (
                      parsedData.skills.map((skill, index) => (
                        <Chip key={index} label={skill} color="primary" variant="outlined" />
                      ))
                    ) : (
                      <Typography variant="body2" color="text.secondary">
                        No skills extracted
                      </Typography>
                    )}
                  </Box>
                </Grid>

                <Grid item xs={12}>
                  <Divider sx={{ my: 2 }} />
                  <Typography variant="h6" gutterBottom>
                    Work Experience
                  </Typography>
                  {parsedData.experience && parsedData.experience.length > 0 ? (
                    parsedData.experience.map((exp, index) => (
                      <Box key={index} sx={{ mb: 2, p: 2, border: '1px solid #e0e0e0', borderRadius: 1 }}>
                        <Typography variant="subtitle1" fontWeight="bold">
                          {exp.title || 'No title provided'}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {(exp.company || 'Company not specified')} • {exp.start_date || 'Date not specified'} - {exp.end_date || 'Present'}
                        </Typography>
                        {exp.description && (
                          <Typography variant="body2" sx={{ mt: 1 }}>
                            {exp.description}
                          </Typography>
                        )}
                      </Box>
                    ))
                  ) : (
                    <Typography variant="body2" color="text.secondary">
                      No experience extracted
                    </Typography>
                  )}
                </Grid>

                <Grid item xs={12}>
                  <Divider sx={{ my: 2 }} />
                  <Typography variant="h6" gutterBottom>
                    Education
                  </Typography>
                  {parsedData.education && parsedData.education.length > 0 ? (
                    parsedData.education.map((edu, index) => (
                      <Box key={index} sx={{ mb: 2, p: 2, border: '1px solid #e0e0e0', borderRadius: 1 }}>
                        <Typography variant="subtitle1" fontWeight="bold">
                          {edu.degree || 'Degree not specified'}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {edu.institution || 'Institution not specified'} • {edu.start_date || 'Date not specified'} - {edu.end_date || 'Present'}
                        </Typography>
                        {edu.field_of_study && (
                          <Typography variant="body2">
                            Field: {edu.field_of_study}
                          </Typography>
                        )}
                      </Box>
                    ))
                  ) : (
                    <Typography variant="body2" color="text.secondary">
                      No education extracted
                    </Typography>
                  )}
                </Grid>
              </Grid>

              <Box sx={{ mt: 3, display: 'flex', justifyContent: 'center', gap: 2 }}>
                <Button 
                  variant="contained" 
                  onClick={handleStartJobHunting}
                  disabled={loading}
                  startIcon={loading ? <CircularProgress size={20} /> : null}
                  size="large"
                >
                  {loading ? 'Creating Session...' : 'Start Job Hunting →'}
                </Button>
                <Button 
                  variant="outlined" 
                  onClick={handleReset}
                  disabled={loading}
                >
                  Upload Another Resume
                </Button>
              </Box>
            </Box>
          )}
        </CardContent>
      </Card>
    </Box>
  );
};

export default ResumeParser;