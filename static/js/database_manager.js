// Database Manager JavaScript
class DatabaseManager {
    constructor() {
        this.currentPage = 1;
        this.pageSize = 20;
        this.totalPages = 1;
        this.filters = {
            search: '',
            platform: '',
            status: '',
            type: ''
        };
        this.charts = {};
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadDashboard();
        this.loadJobs();
    }

    bindEvents() {
        // Refresh button
        document.getElementById('refreshBtn').addEventListener('click', () => {
            this.loadDashboard();
            this.loadJobs();
        });

        // Export button
        document.getElementById('exportBtn').addEventListener('click', () => {
            this.exportData();
        });

        // Search and filters
        document.getElementById('searchInput').addEventListener('input', (e) => {
            this.filters.search = e.target.value;
            this.currentPage = 1;
            this.loadJobs();
        });

        document.getElementById('platformFilter').addEventListener('change', (e) => {
            this.filters.platform = e.target.value;
            this.currentPage = 1;
            this.loadJobs();
        });

        document.getElementById('statusFilter').addEventListener('change', (e) => {
            this.filters.status = e.target.value;
            this.currentPage = 1;
            this.loadJobs();
        });

        document.getElementById('typeFilter').addEventListener('change', (e) => {
            this.filters.type = e.target.value;
            this.currentPage = 1;
            this.loadJobs();
        });

        // Pagination
        document.getElementById('prevPage').addEventListener('click', () => {
            if (this.currentPage > 1) {
                this.currentPage--;
                this.loadJobs();
            }
        });

        document.getElementById('nextPage').addEventListener('click', () => {
            if (this.currentPage < this.totalPages) {
                this.currentPage++;
                this.loadJobs();
            }
        });
    }

    async loadDashboard() {
        try {
            const response = await fetch('/api/dashboard/stats');
            const data = await response.json();
            
            document.getElementById('totalJobs').textContent = data.totalJobs || 0;
            document.getElementById('activeJobs').textContent = data.activeJobs || 0;
            document.getElementById('weekJobs').textContent = data.weekJobs || 0;
            document.getElementById('growthRate').textContent = data.growthRate || '0%';
            
            this.loadCharts(data);
        } catch (error) {
            console.error('Error loading dashboard:', error);
            this.showNotification('Error loading dashboard data', 'error');
        }
    }

    async loadJobs() {
        try {
            const params = new URLSearchParams({
                page: this.currentPage,
                page_size: this.pageSize,
                search: this.filters.search,
                platform: this.filters.platform,
                status: this.filters.status,
                type: this.filters.type
            });

            const response = await fetch(`/api/jobs?${params}`);
            const data = await response.json();
            
            this.renderJobsTable(data.jobs);
            this.updatePagination(data.total, data.page, data.pages);
        } catch (error) {
            console.error('Error loading jobs:', error);
            this.showNotification('Error loading jobs', 'error');
        }
    }

    renderJobsTable(jobs) {
        const tbody = document.getElementById('jobsTableBody');
        tbody.innerHTML = '';

        if (jobs.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="8" class="px-6 py-12 text-center text-gray-500">
                        <i class="fas fa-search text-4xl mb-4"></i>
                        <p>No jobs found matching your criteria</p>
                    </td>
                </tr>
            `;
            return;
        }

        jobs.forEach(job => {
            const row = document.createElement('tr');
            row.className = 'hover:bg-gray-50';
            row.innerHTML = `
                <td class="px-6 py-4 whitespace-nowrap">
                    <div class="text-sm font-medium text-gray-900">${job.title || 'N/A'}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <div class="text-sm text-gray-900">${job.company || 'N/A'}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">
                        ${job.platform || 'N/A'}
                    </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${job.location || 'N/A'}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${job.salary || 'N/A'}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${this.formatDate(job.posted_date)}</td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${this.getStatusColor(job.status)}">
                        ${job.status || 'Unknown'}
                    </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <button onclick="dbManager.viewJobDetails(${job.id})" class="text-blue-600 hover:text-blue-900 mr-2">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button onclick="dbManager.editJob(${job.id})" class="text-green-600 hover:text-green-900 mr-2">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button onclick="dbManager.deleteJob(${job.id})" class="text-red-600 hover:text-red-900">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            `;
            tbody.appendChild(row);
        });
    }

    updatePagination(total, page, pages) {
        this.totalPages = pages;
        
        document.getElementById('showingFrom').textContent = ((page - 1) * this.pageSize) + 1;
        document.getElementById('showingTo').textContent = Math.min(page * this.pageSize, total);
        document.getElementById('totalResults').textContent = total;
        
        document.getElementById('prevPage').disabled = page <= 1;
        document.getElementById('nextPage').disabled = page >= pages;
    }

    loadCharts(data) {
        // Platform Chart
        const platformCtx = document.getElementById('platformChart').getContext('2d');
        if (this.charts.platform) this.charts.platform.destroy();
        
        this.charts.platform = new Chart(platformCtx, {
            type: 'doughnut',
            data: {
                labels: Object.keys(data.platformStats || {}),
                datasets: [{
                    data: Object.values(data.platformStats || {}),
                    backgroundColor: [
                        '#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });

        // Timeline Chart
        const timelineCtx = document.getElementById('timelineChart').getContext('2d');
        if (this.charts.timeline) this.charts.timeline.destroy();
        
        this.charts.timeline = new Chart(timelineCtx, {
            type: 'line',
            data: {
                labels: Object.keys(data.timelineStats || {}),
                datasets: [{
                    label: 'Jobs Posted',
                    data: Object.values(data.timelineStats || {}),
                    borderColor: '#3B82F6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    async viewJobDetails(jobId) {
        try {
            const response = await fetch(`/api/jobs/${jobId}`);
            const job = await response.json();
            
            // Create modal content
            const modalContent = `
                <div class="space-y-4">
                    <div>
                        <h4 class="font-semibold text-gray-900">Job Details</h4>
                        <p><strong>Title:</strong> ${job.title}</p>
                        <p><strong>Company:</strong> ${job.company}</p>
                        <p><strong>Location:</strong> ${job.location}</p>
                        <p><strong>Salary:</strong> ${job.salary}</p>
                        <p><strong>Type:</strong> ${job.type}</p>
                        <p><strong>Platform:</strong> ${job.platform}</p>
                    </div>
                    <div>
                        <h4 class="font-semibold text-gray-900">Description</h4>
                        <p class="text-sm text-gray-600">${job.description || 'No description available'}</p>
                    </div>
                    <div>
                        <h4 class="font-semibold text-gray-900">Requirements</h4>
                        <p class="text-sm text-gray-600">${job.requirements || 'No requirements listed'}</p>
                    </div>
                    <div>
                        <h4 class="font-semibold text-gray-900">Posted</h4>
                        <p class="text-sm text-gray-600">${this.formatDate(job.posted_date)}</p>
                    </div>
                </div>
            `;
            
            this.showModal('Job Details', modalContent);
        } catch (error) {
            console.error('Error loading job details:', error);
            this.showNotification('Error loading job details', 'error');
        }
    }

    async editJob(jobId) {
        // Implementation for editing job
        this.showNotification('Edit functionality coming soon', 'info');
    }

    async deleteJob(jobId) {
        if (confirm('Are you sure you want to delete this job?')) {
            try {
                const response = await fetch(`/api/jobs/${jobId}`, {
                    method: 'DELETE'
                });
                
                if (response.ok) {
                    this.showNotification('Job deleted successfully', 'success');
                    this.loadJobs();
                } else {
                    this.showNotification('Error deleting job', 'error');
                }
            } catch (error) {
                console.error('Error deleting job:', error);
                this.showNotification('Error deleting job', 'error');
            }
        }
    }

    async exportData() {
        try {
            const params = new URLSearchParams(this.filters);
            const response = await fetch(`/api/jobs/export?${params}`);
            const blob = await response.blob();
            
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `jobs_export_${new Date().toISOString().split('T')[0]}.csv`;
            a.click();
            window.URL.revokeObjectURL(url);
            
