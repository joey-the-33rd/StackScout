// Database Manager JavaScript
class DatabaseManager {
    constructor() {
        this.currentPage = 1;
        this.pageSize = 20;
        this.totalPages = 1;
        this.jobs = [];
        this.filteredJobs = [];
        this.charts = {};
        
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadData();
        this.setupCharts();
    }

    bindEvents() {
        document.getElementById('refreshBtn')?.addEventListener('click', () => this.refreshData());
        document.getElementById('exportBtn')?.addEventListener('click', () => this.exportData());
        document.getElementById('searchInput')?.addEventListener('input', () => this.filterJobs());
        document.getElementById('platformFilter')?.addEventListener('change', () => this.filterJobs());
        document.getElementById('statusFilter')?.addEventListener('change', () => this.filterJobs());
        document.getElementById('typeFilter')?.addEventListener('change', () => this.filterJobs());
        document.getElementById('prevPage')?.addEventListener('click', () => this.changePage(-1));
        document.getElementById('nextPage')?.addEventListener('click', () => this.changePage(1));
        document.getElementById('closeModal')?.addEventListener('click', () => this.closeModal());
    }

    async loadData() {
        try {
            const response = await fetch('/api/database/stats');
            const data = await response.json();
            
            this.updateStats(data.stats);
            this.jobs = data.jobs || [];
            this.filteredJobs = [...this.jobs];
            this.renderTable();
            this.updateCharts(data.charts);
        } catch (error) {
            console.error('Error loading data:', error);
            this.showNotification('Error loading data', 'error');
        }
    }

    updateStats(stats) {
        document.getElementById('totalJobs').textContent = stats.totalJobs || 0;
        document.getElementById('activeJobs').textContent = stats.activeJobs || 0;
        document.getElementById('weekJobs').textContent = stats.weekJobs || 0;
        document.getElementById('growthRate').textContent = `${stats.growthRate || 0}%`;
    }

    filterJobs() {
        const searchTerm = document.getElementById('searchInput')?.value.toLowerCase() || '';
        const platformFilter = document.getElementById('platformFilter')?.value || '';
        const statusFilter = document.getElementById('statusFilter')?.value || '';
        const typeFilter = document.getElementById('typeFilter')?.value || '';

        this.filteredJobs = this.jobs.filter(job => {
            const matchesSearch = !searchTerm || 
                job.title.toLowerCase().includes(searchTerm) ||
                job.company.toLowerCase().includes(searchTerm) ||
                job.description.toLowerCase().includes(searchTerm);
            
            const matchesPlatform = !platformFilter || job.platform === platformFilter;
            const matchesStatus = !statusFilter || job.status === statusFilter;
            const matchesType = !typeFilter || job.type === typeFilter;

            return matchesSearch && matchesPlatform && matchesStatus && matchesType;
        });

        this.currentPage = 1;
        this.renderTable();
    }

    renderTable() {
        const tbody = document.getElementById('jobsTableBody');
        if (!tbody) return;

        const start = (this.currentPage - 1) * this.pageSize;
        const end = start + this.pageSize;
        const pageJobs = this.filteredJobs.slice(start, end);

        tbody.innerHTML = pageJobs.map(job => `
            <tr class="hover:bg-gray-50">
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
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${job.location || 'Remote'}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${job.salary || 'N/A'}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${this.formatDate(job.posted_date)}</td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${this.getStatusColor(job.status)}">
                        ${job.status || 'Active'}
                    </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <button onclick="dbManager.viewJob(${job.id})" class="text-blue-600 hover:text-blue-900 mr-2">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button onclick="dbManager.editJob(${job.id})" class="text-green-600 hover:text-green-900 mr-2">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button onclick="dbManager.deleteJob(${job.id})" class="text-red-600 hover:text-red-900">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            </tr>
        `).join('');

        this.updatePagination();
    }

    getStatusColor(status) {
        const colors = {
            'active': 'bg-green-100 text-green-800',
            'expired': 'bg-yellow-100 text-yellow-800',
            'closed': 'bg-red-100 text-red-800'
        };
        return colors[status] || 'bg-gray-100 text-gray-800';
    }

    formatDate(dateString) {
        if (!dateString) return 'N/A';
        const date = new Date(dateString);
        return date.toLocaleDateString();
    }

    updatePagination() {
        const totalResults = this.filteredJobs.length;
        const from = Math.min((this.currentPage - 1) * this.pageSize + 1, totalResults);
        const to = Math.min(this.currentPage * this.pageSize, totalResults);

        document.getElementById('showingFrom').textContent = from;
        document.getElementById('showingTo').textContent = to;
        document.getElementById('totalResults').textContent = totalResults;

        this.totalPages = Math.ceil(totalResults / this.pageSize);
        
        document.getElementById('prevPage').disabled = this.currentPage <= 1;
        document.getElementById('nextPage').disabled = this.currentPage >= this.totalPages;
    }

    changePage(direction) {
        const newPage = this.currentPage + direction;
        if (newPage >= 1 && newPage <= this.totalPages) {
            this.currentPage = newPage;
            this.renderTable();
        }
    }

    setupCharts() {
        const platformCtx = document.getElementById('platformChart');
        const timelineCtx = document.getElementById('timelineChart');

        if (platformCtx) {
            this.charts.platform = new Chart(platformCtx, {
                type: 'doughnut',
                data: {
                    labels: [],
                    datasets: [{
                        data: [],
                        backgroundColor: [
                            '#3B82F6',
                            '#10B981',
                            '#F59E0B',
                            '#EF4444',
                            '#8B5CF6'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false
                }
            });
        }

        if (timelineCtx) {
            this.charts.timeline = new Chart(timelineCtx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Jobs Added',
                        data: [],
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
    }

    updateCharts(chartsData) {
        if (this.charts.platform && chartsData.platform) {
            this.charts.platform.data.labels = Object.keys(chartsData.platform);
            this.charts.platform.data.datasets[0].data = Object.values(chartsData.platform);
            this.charts.platform.update();
        }

        if (this.charts.timeline && chartsData.timeline) {
            this.charts.timeline.data.labels = Object.keys(chartsData.timeline);
            this.charts.timeline.data.datasets[0].data = Object.values(chartsData.timeline);
            this.charts.timeline.update();
        }
    }

    async refreshData() {
        await this.loadData();
        this.showNotification('Data refreshed successfully', 'success');
    }

    async exportData() {
        try {
            const response = await fetch('/api/database/export');
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `stackscout_jobs_${new Date().toISOString().split('T')[0]}.csv`;
            a.click();
            window.URL.revokeObjectURL(url);
            this.showNotification('Data exported successfully', 'success');
        } catch (error) {
            console.error('Error exporting data:', error);
            this.showNotification('Error exporting data', 'error');
        }
    }

    async viewJob(jobId) {
        try {
            const response = await fetch(`/api/database/job/${jobId}`);
            const job = await response.json();
            this.showJobModal(job);
        } catch (error) {
            console.error('Error loading job:', error);
            this.showNotification('Error loading job details', 'error');
        }
    }

    showJobModal(job) {
        const modal = document.getElementById('jobModal');
        const content = document.getElementById('modalContent');
        
        if (!modal || !content) return;

        content.innerHTML = `
            <div class="space-y-4">
                <div>
                    <h4 class="font-semibold text-gray-900">Job Details</h4>
                    <p><strong>Title:</strong> ${job.title || 'N/A'}</p>
                    <p><strong>Company:</strong> ${job.company || 'N/A'}</p>
                    <p><strong>Location:</strong> ${job.location || 'Remote'}</p>
                    <p><strong>Salary:</strong> ${job.salary || 'N/A'}</p>
                    <p><strong>Type:</strong> ${job.type || 'N/A'}</p>
                    <p><strong>Platform:</strong> ${job.platform || 'N/A'}</p>
                    <p><strong>Posted:</strong> ${this.formatDate(job.posted_date)}</p>
                    <p><strong>Status:</strong> ${job.status || 'Active'}</p>
                </div>
                <div>
                    <h4 class="font-semibold text-gray-900">Description</h4>
                    <p class="text-gray-600">${job.description || 'No description available'}</p>
                </div>
                <div>
                    <h4 class="font-semibold text-gray-900">Requirements</h4>
                    <p class="text-gray-600">${job.requirements || 'No requirements listed'}</p>
                </div>
                <div>
                    <h4 class="font-semibold text-gray-900">URL</h4>
                    <a href="${job.url}" target="_blank" class="text-blue-600 hover:underline">${job.url}</a>
                </div>
            </div>
        `;

        modal.classList.remove('hidden');
    }

    closeModal() {
        document.getElementById('jobModal')?.classList.add('hidden');
    }

    async deleteJob(jobId) {
        if (!confirm('Are you sure you want to delete this job?')) return;

        try {
            const response = await fetch(`/api/database/job/${jobId}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                this.showNotification('Job deleted successfully', 'success');
                this.loadData();
            }
        } catch (error) {
            console.error('Error deleting job:', error);
            this.showNotification('Error deleting job', 'error');
        }
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg text-white ${
            type === 'success' ? 'bg-green-500' : 
            type === 'error' ? 'bg-red-500' : 'bg-blue-500'
        }`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
}

// Initialize the database manager
const dbManager = new DatabaseManager();
